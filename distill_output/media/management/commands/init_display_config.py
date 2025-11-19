from django.core.management.base import BaseCommand
from listings.models import DisplayConfig


class Command(BaseCommand):
    help = "Initialize the Display Configuration singleton"

    def handle(self, *args, **options):
        config = DisplayConfig.get_config()
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Display Configuration initialized:\n"
                f"  - Max Listings: {config.max_listings}\n"
                f"  - Max Grocery Stores: {config.max_grocery_stores}\n"
                f"  - Max Clothing Stores: {config.max_clothing_stores}\n"
                f"  - Max Metro Stations: {config.max_metro_stations}"
            )
        )
