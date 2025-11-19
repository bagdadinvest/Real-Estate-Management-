import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point

from listings.models import Listing


EXAMPLE_AREAS = [
    ("Taksim", 41.0369, 28.9850),
    ("Besiktas", 41.0430, 29.0094),
    ("Ortakoy", 41.0479, 29.0264),
    ("Levent", 41.0820, 29.0094),
    ("Uskudar", 41.0255, 29.0150),
    ("Kadikoy", 40.9910, 29.0360),
    ("Moda", 40.9846, 29.0281),
    ("Atasehir", 40.9929, 29.1240),
    ("Erenkoy", 40.9715, 29.0695),
    ("Bostanci", 40.9710, 29.1070),
    ("Sariyer", 41.1680, 29.0490),
    ("Bakirkoy", 40.9806, 28.8721),
]


class Command(BaseCommand):
    help = "Create curated example listings across Istanbul (no images)."

    def add_arguments(self, parser):  # pragma: no cover - simple CLI
        parser.add_argument("--count", type=int, default=len(EXAMPLE_AREAS), help="How many examples to create")

    def handle(self, *args, **options):
        count = options["count"]
        created = 0
        for i in range(count):
            name, lat, lon = EXAMPLE_AREAS[i % len(EXAMPLE_AREAS)]
            # small random jitter to avoid identical points
            lat += random.uniform(-0.0015, 0.0015)
            lon += random.uniform(-0.0015, 0.0015)
            price = random.randrange(3_000_000, 18_000_000, 50_000)
            size = random.randrange(55, 240, 5)

            Listing.objects.create(
                title=f"{name} Example #{i+1}",
                price=price,
                size_sqm=size,
                location=Point(lon, lat, srid=4326),
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} example listings."))

