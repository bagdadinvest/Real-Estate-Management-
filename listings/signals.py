from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Listing

try:
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
except Exception:
    Nominatim = None
    RateLimiter = None


def _full_address(instance: Listing, country_hint: str = "") -> str:
    parts = [instance.address, instance.city, instance.state, instance.zipcode]
    if country_hint:
        parts.append(country_hint)
    return ", ".join([p for p in parts if p])


@receiver(pre_save, sender=Listing)
def clear_coords_on_address_change(sender, instance: Listing, **kwargs):
    if not instance.pk:
        return
    try:
        old = Listing.objects.get(pk=instance.pk)
    except Listing.DoesNotExist:
        return
    addr_changed = any([
        old.address != instance.address,
        old.city != instance.city,
        old.state != instance.state,
        old.zipcode != instance.zipcode,
    ])
    if addr_changed:
        instance.latitude = None
        instance.longitude = None


@receiver(post_save, sender=Listing)
def geocode_if_missing(sender, instance: Listing, created, **kwargs):
    if instance.latitude is not None and instance.longitude is not None:
        return

    # Only attempt when geopy is available
    if Nominatim is None:
        return

    # Basic guard: need enough address info
    if not any([instance.address, instance.city, instance.state, instance.zipcode]):
        return

    try:
        geolocator = Nominatim(user_agent='coralcity_geocoder_signal')
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.0)
        query = _full_address(instance)
        location = geocode(query)
        if location is None:
            return
        Listing.objects.filter(pk=instance.pk).update(
            latitude=location.latitude,
            longitude=location.longitude,
        )
    except Exception:
        # Swallow errors to avoid breaking save paths
        return

