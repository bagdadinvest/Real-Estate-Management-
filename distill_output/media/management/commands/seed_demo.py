import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point

from listings.models import Listing
from transit_layer.models import MetroStation, BusStop


KADIKOY_BBOX = {
    "min_lat": 40.9800,
    "max_lat": 41.0100,
    "min_lon": 29.0200,
    "max_lon": 29.0600,
}


METRO_STATIONS = [
    ("Kadikoy", 29.0256, 40.9900),
    ("Sogutlucesme", 29.0286, 40.9950),
    ("Ayrilik Cesmesi", 29.0245, 41.0040),
    ("Acibadem", 29.0462, 41.0052),
    ("Unalan", 29.0430, 41.0100),
    ("Goztepe", 29.0590, 40.9923),
    ("Yenisahra", 29.0860, 40.9910),
    ("Kozyatagi", 29.0990, 40.9830),
    ("Bostanci", 29.1070, 40.9760),
]


class Command(BaseCommand):
    help = "Seed demo data: metro stations and sample listings in Kadikoy"

    def add_arguments(self, parser):  # pragma: no cover - simple CLI
        parser.add_argument("--listings", type=int, default=15, help="Number of listings to create")

    def handle(self, *args, **options):
        count = options["listings"]

        # Seed MetroStations (idempotent by name)
        created_stations = 0
        for name, lon, lat in METRO_STATIONS:
            obj, created = MetroStation.objects.get_or_create(
                name=name,
                defaults={"location": Point(lon, lat, srid=4326)},
            )
            created_stations += 1 if created else 0

        # Seed Listings
        created_listings = 0
        for i in range(count):
            lat = random.uniform(KADIKOY_BBOX["min_lat"], KADIKOY_BBOX["max_lat"])
            lon = random.uniform(KADIKOY_BBOX["min_lon"], KADIKOY_BBOX["max_lon"])
            price = random.randrange(2_500_000, 12_000_000, 50_000)
            size = random.randrange(45, 220, 5)

            Listing.objects.create(
                title=f"Sample Listing #{i+1}",
                price=price,
                size_sqm=size,
                location=Point(lon, lat, srid=4326),
            )
            created_listings += 1

        # Seed Bus Stops (10 random within bbox)
        created_bus = 0
        for i in range(10):
            lat = random.uniform(KADIKOY_BBOX["min_lat"], KADIKOY_BBOX["max_lat"])
            lon = random.uniform(KADIKOY_BBOX["min_lon"], KADIKOY_BBOX["max_lon"])
            BusStop.objects.create(
                name=f"Bus Stop #{i+1}",
                location=Point(lon, lat, srid=4326),
            )
            created_bus += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_stations} metro stations (new or existing), {created_listings} listings, and {created_bus} bus stops."
            )
        )
