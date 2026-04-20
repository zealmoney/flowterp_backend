from django.core.management.base import BaseCommand

from states.models import CreativeState


class Command(BaseCommand):
    help = "Seed the FlowTerp 12-state creative system"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding FlowTerp 12-state system..."))

        states_data = [
            {
                "name": "Deep Focus",
                "description": (
                    "A concentrated state designed for extended attention, mental clarity, "
                    "and distraction-free execution."
                ),
                "intended_use": (
                    "writing complex code, solving technical problems, focused work sessions, "
                    "structured editing"
                ),
            },
            {
                "name": "Debugging Mode",
                "description": (
                    "A patient and analytical state designed for troubleshooting, review, "
                    "and identifying hidden issues."
                ),
                "intended_use": (
                    "debugging code, tracing issues, reviewing logs, fixing workflow problems"
                ),
            },
            {
                "name": "System Design Thinking",
                "description": (
                    "A strategic and big-picture state designed for planning systems, "
                    "mapping architecture, and organizing complex ideas."
                ),
                "intended_use": (
                    "API planning, database design, product architecture, technical strategy"
                ),
            },
            {
                "name": "Creative Flow",
                "description": (
                    "An expressive state designed for momentum, experimentation, and freeform "
                    "creative output."
                ),
                "intended_use": (
                    "idea generation, freestyle creation, concept building, artistic exploration"
                ),
            },
            {
                "name": "Music Production Mode",
                "description": (
                    "A balanced state designed for building tracks, arranging layers, "
                    "and staying musically productive."
                ),
                "intended_use": (
                    "beat making, arranging songs, composing, layering instruments and vocals"
                ),
            },
            {
                "name": "Sound Design Mode",
                "description": (
                    "An experimental and detail-oriented state designed for crafting textures, "
                    "effects, and immersive sound."
                ),
                "intended_use": (
                    "sound design, creating FX, sculpting synths, cinematic audio work, foley"
                ),
            },
            {
                "name": "Cinematic Review",
                "description": (
                    "A calm and visually sensitive state designed for reviewing pacing, mood, "
                    "visual feel, and emotional impact."
                ),
                "intended_use": (
                    "reviewing edits, color grading, final cut review, soundtrack review, scene polish"
                ),
            },
            {
                "name": "Editing Mode",
                "description": (
                    "A responsive and task-driven state designed for sequencing, cutting, "
                    "and shaping content efficiently."
                ),
                "intended_use": (
                    "video editing, timeline work, pacing adjustments, clip sequencing, assembly cuts"
                ),
            },
            {
                "name": "Storyboarding Mind",
                "description": (
                    "A visual planning state designed for mapping scenes, exploring story beats, "
                    "and organizing cinematic ideas."
                ),
                "intended_use": (
                    "storyboarding, scene planning, shot design, concept visualization, narrative structure"
                ),
            },
            {
                "name": "Idea Generation",
                "description": (
                    "An open and expansive state designed for brainstorming, concept development, "
                    "and discovering fresh directions."
                ),
                "intended_use": (
                    "brainstorming, writing concepts, naming ideas, creative planning, ideation"
                ),
            },
            {
                "name": "Relaxed Creativity",
                "description": (
                    "A low-pressure creative state designed for calm exploration, easy experimentation, "
                    "and smooth creative sessions."
                ),
                "intended_use": (
                    "light creative work, casual production, sketching ideas, relaxed sessions"
                ),
            },
            {
                "name": "Late Night Vibes",
                "description": (
                    "An immersive and atmospheric state designed for introspective work, "
                    "night sessions, and emotionally rich creation."
                ),
                "intended_use": (
                    "late-night music production, solo editing, immersive coding, nighttime creation"
                ),
            },
        ]

        created_count = 0
        updated_count = 0

        for item in states_data:
            state, created = CreativeState.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "intended_use": item["intended_use"],
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"FlowTerp 12-state system seeded successfully. "
                f"Created: {created_count}, Updated: {updated_count}"
            )
        )