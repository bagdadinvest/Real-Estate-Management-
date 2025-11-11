import time
from django.core.management.base import BaseCommand
from django.db.models import Q
from listings.models import Listing

try:
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
except Exception:  # geopy may not be installed yet
    Nominatim = None
    RateLimiter = None


class Command(BaseCommand):
    help = "Geocode listings without coordinates using Nominatim (OpenStreetMap)."

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='Geocode all listings (overwrite existing lat/lng).')
        parser.add_argument('--country', default='', help='Optional country to append to queries (e.g., "Nigeria").')
        parser.add_argument('--sleep', type=float, default=1.1, help='Seconds to sleep between requests (rate limiting).')

    def handle(self, *args, **options):
        if Nominatim is None:
            self.stderr.write(self.style.ERROR('geopy is not installed. Install it with "pip install geopy".'))
            return

        qs = Listing.objects.all()
        if not options['all']:
            qs = qs.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))

        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No listings need geocoding.'))
            return

        geolocator = Nominatim(user_agent='coralcity_geocoder')
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=options['sleep'])

        processed = 0
        for listing in qs.iterator():
            query = ", ".join(filter(None, [
                listing.address,
                listing.city,
                listing.state,
                listing.zipcode,
                options['country'],
            ]))

            try:
                location = geocode(query)
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"Geocoding error for id={listing.id}: {e}"))
                continue

            if location is None:
                self.stderr.write(self.style.WARNING(f"No result for id={listing.id} | query='{query}'"))
                continue

            listing.latitude = location.latitude
            listing.longitude = location.longitude
            listing.save(update_fields=['latitude', 'longitude'])
            processed += 1
            self.stdout.write(self.style.SUCCESS(f"Geocoded id={listing.id} -> ({listing.latitude}, {listing.longitude})"))

        self.stdout.write(self.style.SUCCESS(f"Done. Geocoded {processed}/{count} listings."))

