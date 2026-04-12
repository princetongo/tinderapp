from django.core.management.base import BaseCommand
from profiles.models import Interest


INTERESTS = [
    ("Travel", "✈️"), ("Photography", "📸"), ("Music", "🎵"), ("Cooking", "🍳"),
    ("Fitness", "💪"), ("Reading", "📚"), ("Gaming", "🎮"), ("Art", "🎨"),
    ("Movies", "🎬"), ("Hiking", "🥾"), ("Dancing", "💃"), ("Coffee", "☕"),
    ("Wine", "🍷"), ("Yoga", "🧘"), ("Dogs", "🐕"), ("Cats", "🐈"),
    ("Cycling", "🚴"), ("Swimming", "🏊"), ("Surfing", "🏄"), ("Foodie", "🍜"),
    ("Meditation", "🧠"), ("Fashion", "👗"), ("Tech", "💻"), ("Sports", "⚽"),
    ("Volunteering", "🤝"), ("Languages", "🗣️"), ("Theatre", "🎭"), ("Comedy", "😂"),
]


class Command(BaseCommand):
    help = 'Seed interests into the database'

    def handle(self, *args, **kwargs):
        created = 0
        for name, emoji in INTERESTS:
            _, was_created = Interest.objects.get_or_create(name=name, defaults={'emoji': emoji})
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Seeded {created} new interests ({len(INTERESTS)} total).'))
