import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

import cloudinary.uploader
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from effects.models import Effect
from states.models import CreativeState
from terpenes.models import Terpene
from strains.models import Strain, StrainEffect, StrainState, StrainTerpene


def parse_decimal(value):
    if value in (None, "", "null"):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def csv_has_value(row, key):
    return key in row and row.get(key) not in [None, ""]


def parse_scored_slugs(raw_value):
    results = []

    if not raw_value:
        return results

    parts = [part.strip() for part in raw_value.split(",") if part.strip()]
    for part in parts:
        if ":" not in part:
            continue

        slug, score = part.split(":", 1)
        slug = slug.strip()
        score_decimal = parse_decimal(score.strip())

        if slug and score_decimal is not None:
            results.append((slug, score_decimal))

    return results


class Command(BaseCommand):
    help = "Bulk import strains and images from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            required=True,
            help="Absolute or relative path to the CSV file.",
        )
        parser.add_argument(
            "--images-dir",
            type=str,
            required=False,
            default="",
            help="Directory containing image files referenced by image_filename.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing strains if they already exist.",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Print row-level debug output.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = Path(options["csv"]).resolve()
        images_dir = Path(options["images_dir"]).resolve() if options["images_dir"] else None
        allow_update = options["update"]
        debug = options["debug"]

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        if images_dir and not images_dir.exists():
            raise CommandError(f"Images directory not found: {images_dir}")

        created_count = 0
        updated_count = 0
        image_uploaded_count = 0
        saw_rows = False

        with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)

            if debug:
                self.stdout.write(self.style.WARNING(f"CSV PATH: {csv_path}"))
                self.stdout.write(self.style.WARNING(f"CSV HEADERS: {reader.fieldnames}"))

            for row_index, row in enumerate(reader, start=2):
                saw_rows = True

                if debug:
                    self.stdout.write(self.style.WARNING(f"ROW {row_index}: {row}"))

                name = (row.get("name") or "").strip()

                if debug:
                    self.stdout.write(self.style.WARNING(f"PARSED NAME: '{name}'"))

                if not name:
                    self.stdout.write(
                        self.style.WARNING(f"Row {row_index}: missing strain name, skipped.")
                    )
                    continue

                strain = Strain.objects.filter(name=name).first()

                if strain and not allow_update:
                    self.stdout.write(
                        self.style.WARNING(f"Row {row_index}: '{name}' already exists, skipped.")
                    )
                    continue

                if not strain:
                    strain = Strain.objects.create(
                        name=name,
                        strain_type=(row.get("strain_type") or "hybrid").strip() or "hybrid",
                        description=(row.get("description") or "").strip(),
                        flavor_profile=(row.get("flavor_profile") or "").strip(),
                        aroma_profile=(row.get("aroma_profile") or "").strip(),
                        thc_min=parse_decimal(row.get("thc_min")),
                        thc_max=parse_decimal(row.get("thc_max")),
                        cbd_min=parse_decimal(row.get("cbd_min")),
                        cbd_max=parse_decimal(row.get("cbd_max")),
                        breeder=(row.get("breeder") or "").strip(),
                        lineage=(row.get("lineage") or "").strip(),
                        is_active=True,
                    )
                    created_count += 1
                else:
                    if csv_has_value(row, "strain_type"):
                        strain.strain_type = row["strain_type"].strip() or strain.strain_type

                    if csv_has_value(row, "description"):
                        strain.description = row["description"].strip()

                    if csv_has_value(row, "flavor_profile"):
                        strain.flavor_profile = row["flavor_profile"].strip()

                    if csv_has_value(row, "aroma_profile"):
                        strain.aroma_profile = row["aroma_profile"].strip()

                    if csv_has_value(row, "thc_min"):
                        strain.thc_min = parse_decimal(row["thc_min"])

                    if csv_has_value(row, "thc_max"):
                        strain.thc_max = parse_decimal(row["thc_max"])

                    if csv_has_value(row, "cbd_min"):
                        strain.cbd_min = parse_decimal(row["cbd_min"])

                    if csv_has_value(row, "cbd_max"):
                        strain.cbd_max = parse_decimal(row["cbd_max"])

                    if csv_has_value(row, "breeder"):
                        strain.breeder = row["breeder"].strip()

                    if csv_has_value(row, "lineage"):
                        strain.lineage = row["lineage"].strip()

                    strain.save()
                    updated_count += 1

                image_filename = (row.get("image_filename") or "").strip()
                if image_filename and images_dir:
                    image_path = images_dir / image_filename

                    if image_path.exists():
                        try:
                            upload_result = cloudinary.uploader.upload(
                                str(image_path),
                                folder="flowterp/strains",
                                public_id=Path(image_filename).stem,
                                overwrite=True,
                                resource_type="image",
                            )

                            strain.image = upload_result["public_id"]
                            strain.save(update_fields=["image", "updated_at"])

                            image_uploaded_count += 1

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Row {row_index}: uploaded image for '{name}'."
                                )
                            )
                        except Exception as exc:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Row {row_index}: failed to upload image for '{name}' -> {exc}"
                                )
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Row {row_index}: image not found for '{name}' -> {image_path}"
                            )
                        )

                if csv_has_value(row, "effects"):
                    StrainEffect.objects.filter(strain=strain).delete()

                    for effect_slug, score in parse_scored_slugs(row.get("effects")):
                        effect = Effect.objects.filter(slug=effect_slug).first()
                        if effect:
                            StrainEffect.objects.create(
                                strain=strain,
                                effect=effect,
                                score=score,
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Row {row_index}: effect slug '{effect_slug}' not found."
                                )
                            )

                if csv_has_value(row, "terpenes"):
                    StrainTerpene.objects.filter(strain=strain).delete()

                    for terpene_slug, prominence in parse_scored_slugs(row.get("terpenes")):
                        terpene = Terpene.objects.filter(slug=terpene_slug).first()
                        if terpene:
                            StrainTerpene.objects.create(
                                strain=strain,
                                terpene=terpene,
                                prominence=prominence,
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Row {row_index}: terpene slug '{terpene_slug}' not found."
                                )
                            )

                if csv_has_value(row, "states"):
                    StrainState.objects.filter(strain=strain).delete()

                    for state_slug, score in parse_scored_slugs(row.get("states")):
                        state = CreativeState.objects.filter(slug=state_slug).first()
                        if state:
                            StrainState.objects.create(
                                strain=strain,
                                state=state,
                                score=score,
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Row {row_index}: state slug '{state_slug}' not found."
                                )
                            )

        if not saw_rows:
            self.stdout.write(self.style.WARNING("No data rows were read from the CSV."))

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Created: {created_count}, Updated: {updated_count}, Images Uploaded: {image_uploaded_count}"
            )
        )