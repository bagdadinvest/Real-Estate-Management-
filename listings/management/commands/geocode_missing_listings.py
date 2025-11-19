from django.core.management.base import BaseCommand
from django.db import close_old_connections
import time

from listings.models import Listing


class Command(BaseCommand):
    help = "Geocode all listings missing coordinates (latitude/longitude)."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0, help="Limit number of listings to process (0 = all)")
        parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between requests")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be geocoded without saving")

    def handle(self, *args, **options):
        limit = int(options.get("limit") or 0)
        sleep_sec = float(options.get("sleep") or 0.0)
        dry_run = bool(options.get("dry_run"))

        qs = Listing.objects.filter(latitude__isnull=True) | Listing.objects.filter(longitude__isnull=True)
        qs = qs.distinct().order_by("id")
        total = qs.count()
        if limit > 0:
            qs = qs[:limit]

        processed = 0
        updated = 0
        for listing in qs:
            processed += 1
            self.stdout.write(f"[{processed}/{total}] Geocoding id={listing.id} title='{listing.title}'")
            if dry_run:
                # Show the full address that would be used
                addr_parts = [listing.address, listing.city, listing.state, listing.zipcode]
                full_addr = ", ".join([p for p in addr_parts if p])
                self.stdout.write(f"  DRY-RUN address='{full_addr}'")
            else:
                try:
                    close_old_connections()
                    # Call the same helper the model uses, but save with skip_geocode to avoid recursion
                    listing.geocode_address()
                    if listing.latitude is not None and listing.longitude is not None:
                        listing.save(skip_geocode=True)
                        updated += 1
                        self.stdout.write(self.style.SUCCESS(f"  OK lat={listing.latitude} lon={listing.longitude}"))
                    else:
                        self.stdout.write(self.style.WARNING("  Not found"))
                finally:
                    close_old_connections()

            if sleep_sec > 0:
                time.sleep(sleep_sec)

        self.stdout.write(self.style.SUCCESS(f"Done. processed={processed}, updated={updated}, total_missing={total}"))

