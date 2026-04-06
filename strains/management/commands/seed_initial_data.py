from decimal import Decimal

from django.core.management.base import BaseCommand

from effects.models import Effect
from states.models import CreativeState
from strains.models import Strain, StrainEffect, StrainState, StrainTerpene, StrainType
from terpenes.models import Terpene


class Command(BaseCommand):
    help = "Seed initial FlowTerp data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding initial FlowTerp data..."))

        effects = self.seed_effects()
        terpenes = self.seed_terpenes()
        states = self.seed_states()
        strains = self.seed_strains()

        self.seed_strain_effects(strains, effects)
        self.seed_strain_terpenes(strains, terpenes)
        self.seed_strain_states(strains, states)

        self.stdout.write(self.style.SUCCESS("Initial FlowTerp data seeded successfully."))

    def seed_effects(self):
        effect_data = [
            {
                "name": "Creative",
                "description": "Commonly associated with idea generation, artistic flow, and imaginative thinking.",
            },
            {
                "name": "Focused",
                "description": "Commonly associated with concentration, clarity, and task execution.",
            },
            {
                "name": "Relaxed",
                "description": "Commonly associated with reduced tension and a calmer body state.",
            },
            {
                "name": "Energetic",
                "description": "Commonly associated with stimulation, momentum, and alertness.",
            },
            {
                "name": "Euphoric",
                "description": "Commonly associated with elevated mood and positive emotional lift.",
            },
            {
                "name": "Sleepy",
                "description": "Commonly associated with sedation and late-night wind-down.",
            },
        ]

        created_effects = {}
        for item in effect_data:
            effect, _ = Effect.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "is_active": True,
                },
            )
            created_effects[effect.name] = effect

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_effects)} effects."))
        return created_effects

    def seed_terpenes(self):
        terpene_data = [
            {
                "name": "Myrcene",
                "description": "Commonly described as earthy and musky; often associated with relaxation.",
                "aroma_profile": "earthy, musky, herbal",
            },
            {
                "name": "Limonene",
                "description": "Commonly described as citrus-forward; often associated with uplift and brightness.",
                "aroma_profile": "citrus, lemon, bright",
            },
            {
                "name": "Caryophyllene",
                "description": "Commonly described as peppery and spicy; often associated with body calm.",
                "aroma_profile": "peppery, spicy, woody",
            },
            {
                "name": "Pinene",
                "description": "Commonly described as pine-forward; often associated with alertness and clarity.",
                "aroma_profile": "pine, fresh, forest",
            },
            {
                "name": "Linalool",
                "description": "Commonly described as floral and lavender-like; often associated with calm.",
                "aroma_profile": "floral, lavender, soft",
            },
            {
                "name": "Humulene",
                "description": "Commonly described as woody and earthy; often associated with grounded effects.",
                "aroma_profile": "woody, earthy, herbal",
            },
        ]

        created_terpenes = {}
        for item in terpene_data:
            terpene, _ = Terpene.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "aroma_profile": item["aroma_profile"],
                    "is_active": True,
                },
            )
            created_terpenes[terpene.name] = terpene

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_terpenes)} terpenes."))
        return created_terpenes

    def seed_states(self):
        state_data = [
            {
                "name": "Deep Focus",
                "description": "A state aimed at concentrated work, problem-solving, and extended attention.",
                "intended_use": "coding, technical work, structured editing, long task sessions",
            },
            {
                "name": "Creative Flow",
                "description": "A state aimed at open-ended ideation, world-building, and artistic momentum.",
                "intended_use": "music production, visual ideation, design, writing, beat creation",
            },
            {
                "name": "Cinematic Review",
                "description": "A state aimed at reviewing work, pacing, visual feel, and emotional impact.",
                "intended_use": "film review, color pass review, sound scoring review, final content review",
            },
            {
                "name": "Energy Boost",
                "description": "A state aimed at increasing momentum, drive, and action-oriented creativity.",
                "intended_use": "brainstorming, energetic sessions, early-day work blocks",
            },
            {
                "name": "Late Night Wind Down",
                "description": "A state aimed at decompressing, reflecting, and slowing the nervous system.",
                "intended_use": "end-of-day relaxation, post-session review, nighttime reset",
            },
        ]

        created_states = {}
        for item in state_data:
            state, _ = CreativeState.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "intended_use": item["intended_use"],
                    "is_active": True,
                },
            )
            created_states[state.name] = state

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_states)} creative states."))
        return created_states

    def seed_strains(self):
        strain_data = [
            {
                "name": "Blue Dream",
                "strain_type": StrainType.HYBRID,
                "description": "A balanced and widely known strain often associated with creative energy and functional daytime use.",
                "flavor_profile": "sweet, berry, herbal",
                "aroma_profile": "berry, earthy, sweet",
                "thc_min": Decimal("17.00"),
                "thc_max": Decimal("24.00"),
                "cbd_min": Decimal("0.00"),
                "cbd_max": Decimal("2.00"),
                "breeder": "",
                "lineage": "Blueberry x Haze",
                "is_featured": True,
            },
            {
                "name": "Durban Poison",
                "strain_type": StrainType.SATIVA,
                "description": "A classic sativa often associated with alertness, momentum, and sharp daytime focus.",
                "flavor_profile": "sweet, spicy, earthy",
                "aroma_profile": "pine, spice, sweet",
                "thc_min": Decimal("18.00"),
                "thc_max": Decimal("26.00"),
                "cbd_min": Decimal("0.00"),
                "cbd_max": Decimal("1.00"),
                "breeder": "",
                "lineage": "Landrace",
                "is_featured": True,
            },
            {
                "name": "Gelato",
                "strain_type": StrainType.HYBRID,
                "description": "A flavorful hybrid often associated with elevated mood, creative immersion, and smooth body calm.",
                "flavor_profile": "sweet, creamy, dessert-like",
                "aroma_profile": "vanilla, citrus, earthy",
                "thc_min": Decimal("20.00"),
                "thc_max": Decimal("27.00"),
                "cbd_min": Decimal("0.00"),
                "cbd_max": Decimal("1.00"),
                "breeder": "",
                "lineage": "Sunset Sherbet x Thin Mint GSC",
                "is_featured": True,
            },
            {
                "name": "Sugar Cookies",
                "strain_type": StrainType.HYBRID,
                "description": "A dessert-leaning hybrid often associated with relaxed creativity and smooth visual review sessions.",
                "flavor_profile": "sweet, vanilla, creamy",
                "aroma_profile": "sugary, earthy, light fruit",
                "thc_min": Decimal("18.00"),
                "thc_max": Decimal("25.00"),
                "cbd_min": Decimal("0.00"),
                "cbd_max": Decimal("1.00"),
                "breeder": "",
                "lineage": "Crystal Gayle x Blue Hawaiian",
                "is_featured": True,
            },
            {
                "name": "Wedding Cake",
                "strain_type": StrainType.HYBRID,
                "description": "A potent hybrid often associated with euphoric immersion and heavier late-session relaxation.",
                "flavor_profile": "sweet, tangy, vanilla",
                "aroma_profile": "earthy, peppery, sweet",
                "thc_min": Decimal("19.00"),
                "thc_max": Decimal("27.00"),
                "cbd_min": Decimal("0.00"),
                "cbd_max": Decimal("1.00"),
                "breeder": "",
                "lineage": "Triangle Kush x Animal Mints",
                "is_featured": True,
            },
            {
                "name": "Granddaddy Purple",
                "strain_type": StrainType.INDICA,
                "description": "A classic indica often associated with body-heavy calm, mood elevation, and deep nighttime relaxation.",
                "flavor_profile": "grape, berry, sweet",
                "aroma_profile": "grape, earthy, sweet",
                "thc_min": Decimal("17.00"),
                "thc_max": Decimal("23.00"),
                "cbd_min": Decimal("0.00"),
                "cbd_max": Decimal("1.00"),
                "breeder": "",
                "lineage": "Purple Urkle x Big Bud",
                "is_featured": False,
            },
        ]

        created_strains = {}
        for item in strain_data:
            strain, _ = Strain.objects.update_or_create(
                name=item["name"],
                defaults={
                    "strain_type": item["strain_type"],
                    "description": item["description"],
                    "flavor_profile": item["flavor_profile"],
                    "aroma_profile": item["aroma_profile"],
                    "thc_min": item["thc_min"],
                    "thc_max": item["thc_max"],
                    "cbd_min": item["cbd_min"],
                    "cbd_max": item["cbd_max"],
                    "breeder": item["breeder"],
                    "lineage": item["lineage"],
                    "is_active": True,
                    "is_featured": item["is_featured"],
                },
            )
            created_strains[strain.name] = strain

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_strains)} strains."))
        return created_strains

    def seed_strain_effects(self, strains, effects):
        strain_effect_map = {
            "Blue Dream": [
                ("Creative", "0.92"),
                ("Focused", "0.86"),
                ("Energetic", "0.80"),
                ("Euphoric", "0.78"),
            ],
            "Durban Poison": [
                ("Focused", "0.95"),
                ("Energetic", "0.94"),
                ("Creative", "0.82"),
            ],
            "Gelato": [
                ("Creative", "0.90"),
                ("Euphoric", "0.88"),
                ("Relaxed", "0.72"),
            ],
            "Sugar Cookies": [
                ("Creative", "0.79"),
                ("Relaxed", "0.88"),
                ("Euphoric", "0.72"),
            ],
            "Wedding Cake": [
                ("Euphoric", "0.89"),
                ("Relaxed", "0.84"),
                ("Creative", "0.70"),
            ],
            "Granddaddy Purple": [
                ("Relaxed", "0.94"),
                ("Sleepy", "0.91"),
                ("Euphoric", "0.68"),
            ],
        }

        count = 0
        for strain_name, linked_effects in strain_effect_map.items():
            strain = strains[strain_name]
            for effect_name, score in linked_effects:
                StrainEffect.objects.update_or_create(
                    strain=strain,
                    effect=effects[effect_name],
                    defaults={
                        "score": Decimal(score),
                        "notes": "",
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {count} strain-effect links."))

    def seed_strain_terpenes(self, strains, terpenes):
        strain_terpene_map = {
            "Blue Dream": [
                ("Myrcene", "0.83"),
                ("Pinene", "0.75"),
                ("Caryophyllene", "0.61"),
            ],
            "Durban Poison": [
                ("Terpinolene", "0.90"),
                ("Pinene", "0.78"),
                ("Limonene", "0.65"),
            ],
            "Gelato": [
                ("Caryophyllene", "0.86"),
                ("Limonene", "0.81"),
                ("Humulene", "0.62"),
            ],
            "Sugar Cookies": [
                ("Myrcene", "0.84"),
                ("Caryophyllene", "0.73"),
                ("Limonene", "0.58"),
            ],
            "Wedding Cake": [
                ("Caryophyllene", "0.88"),
                ("Limonene", "0.72"),
                ("Linalool", "0.55"),
            ],
            "Granddaddy Purple": [
                ("Myrcene", "0.91"),
                ("Linalool", "0.70"),
                ("Caryophyllene", "0.60"),
            ],
        }

        if "Terpinolene" not in terpenes:
            terpinolene, _ = Terpene.objects.update_or_create(
                name="Terpinolene",
                defaults={
                    "description": "Commonly described as fresh and complex; often associated with an energetic or uplifting profile.",
                    "aroma_profile": "fresh, herbal, citrusy",
                    "is_active": True,
                },
            )
            terpenes["Terpinolene"] = terpinolene

        count = 0
        for strain_name, linked_terpenes in strain_terpene_map.items():
            strain = strains[strain_name]
            for terpene_name, prominence in linked_terpenes:
                StrainTerpene.objects.update_or_create(
                    strain=strain,
                    terpene=terpenes[terpene_name],
                    defaults={
                        "prominence": Decimal(prominence),
                        "notes": "",
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {count} strain-terpene links."))

    def seed_strain_states(self, strains, states):
        strain_state_map = {
            "Blue Dream": [
                ("Creative Flow", "0.93", "afternoon"),
                ("Deep Focus", "0.84", "morning"),
                ("Energy Boost", "0.80", "midday"),
            ],
            "Durban Poison": [
                ("Deep Focus", "0.96", "morning"),
                ("Energy Boost", "0.94", "morning"),
                ("Creative Flow", "0.78", "midday"),
            ],
            "Gelato": [
                ("Creative Flow", "0.91", "evening"),
                ("Cinematic Review", "0.86", "late-night"),
            ],
            "Sugar Cookies": [
                ("Cinematic Review", "0.92", "late-night"),
                ("Creative Flow", "0.77", "evening"),
                ("Late Night Wind Down", "0.74", "night"),
            ],
            "Wedding Cake": [
                ("Cinematic Review", "0.88", "night"),
                ("Late Night Wind Down", "0.82", "night"),
                ("Creative Flow", "0.69", "evening"),
            ],
            "Granddaddy Purple": [
                ("Late Night Wind Down", "0.96", "night"),
                ("Cinematic Review", "0.66", "late-night"),
            ],
        }

        count = 0
        for strain_name, linked_states in strain_state_map.items():
            strain = strains[strain_name]
            for state_name, score, best_time in linked_states:
                StrainState.objects.update_or_create(
                    strain=strain,
                    state=states[state_name],
                    defaults={
                        "score": Decimal(score),
                        "best_time_of_day": best_time,
                        "notes": "",
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {count} strain-state links."))