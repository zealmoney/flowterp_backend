from decimal import Decimal

from django.core.management.base import BaseCommand

from states.models import CreativeState
from strains.models import Strain, StrainState


class Command(BaseCommand):
    help = "Seed FlowTerp strain-to-state recommendation scores"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding FlowTerp strain-to-state scores..."))

        strain_state_map = {
            "Blue Dream": [
                ("Creative Flow", "0.93", "afternoon"),
                ("Deep Focus", "0.84", "morning"),
                ("Idea Generation", "0.89", "midday"),
                ("Editing Mode", "0.82", "afternoon"),
                ("Relaxed Creativity", "0.76", "evening"),
            ],
            "Durban Poison": [
                ("Deep Focus", "0.96", "morning"),
                ("Debugging Mode", "0.91", "morning"),
                ("System Design Thinking", "0.88", "midday"),
                ("Editing Mode", "0.81", "midday"),
                ("Idea Generation", "0.78", "afternoon"),
            ],
            "Gelato": [
                ("Creative Flow", "0.91", "evening"),
                ("Music Production Mode", "0.88", "evening"),
                ("Sound Design Mode", "0.82", "night"),
                ("Cinematic Review", "0.86", "late-night"),
                ("Relaxed Creativity", "0.80", "night"),
                ("Late Night Vibes", "0.84", "night"),
            ],
            "Sugar Cookies": [
                ("Cinematic Review", "0.92", "late-night"),
                ("Creative Flow", "0.77", "evening"),
                ("Relaxed Creativity", "0.86", "night"),
                ("Late Night Vibes", "0.88", "night"),
                ("Storyboarding Mind", "0.75", "evening"),
            ],
            "Wedding Cake": [
                ("Cinematic Review", "0.88", "night"),
                ("Late Night Vibes", "0.90", "night"),
                ("Relaxed Creativity", "0.82", "night"),
                ("Music Production Mode", "0.73", "evening"),
                ("Sound Design Mode", "0.71", "night"),
            ],
            "Granddaddy Purple": [
                ("Late Night Vibes", "0.96", "night"),
                ("Relaxed Creativity", "0.90", "night"),
                ("Cinematic Review", "0.66", "late-night"),
            ],
        }

        missing_strains = []
        missing_states = set()
        created_count = 0
        updated_count = 0

        for strain_name, linked_states in strain_state_map.items():
            strain = Strain.objects.filter(name=strain_name).first()

            if not strain:
                missing_strains.append(strain_name)
                continue

            for state_name, score, best_time in linked_states:
                state = CreativeState.objects.filter(name=state_name).first()

                if not state:
                    missing_states.add(state_name)
                    continue

                _, created = StrainState.objects.update_or_create(
                    strain=strain,
                    state=state,
                    defaults={
                        "score": Decimal(score),
                        "best_time_of_day": best_time,
                        "notes": "",
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        if missing_strains:
            self.stdout.write(
                self.style.WARNING(
                    f"Missing strains: {', '.join(sorted(set(missing_strains)))}"
                )
            )

        if missing_states:
            self.stdout.write(
                self.style.WARNING(
                    f"Missing states: {', '.join(sorted(missing_states))}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Strain-to-state scores seeded successfully. "
                f"Created: {created_count}, Updated: {updated_count}"
            )
        )