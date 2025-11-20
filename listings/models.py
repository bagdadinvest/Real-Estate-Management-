from django.db import models
from datetime import datetime
from django.utils.timezone import timezone
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

from realtors.models import Realtor
import os

# Create your models here.

class Listing(models.Model):
    realtor = models.ForeignKey(Realtor, on_delete=models.DO_NOTHING, blank=True)
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    # Deal type: rent/sell/buy
    deal_type = models.CharField(max_length=10, blank=True)
    # Real estate type (e.g., Apartment/Daire, Villa, etc.)
    property_type = models.CharField(max_length=50, blank=True)
    bathrooms = models.IntegerField()
    garage = models.IntegerField(default=0)
    sqft = models.IntegerField()
    lot_size = models.DecimalField(max_digits=6, decimal_places=1, default=0.0)
    # New reference fields from source
    external_id = models.CharField(max_length=64, blank=True, db_index=True)
    ad_date = models.DateField(null=True, blank=True)
    # Details
    m2_gross = models.IntegerField(null=True, blank=True)
    m2_net = models.IntegerField(null=True, blank=True)
    rooms_text = models.CharField(max_length=20, blank=True)
    building_age = models.IntegerField(null=True, blank=True)
    floor_number = models.IntegerField(null=True, blank=True)
    floors_total = models.IntegerField(null=True, blank=True)
    heating = models.CharField(max_length=100, blank=True)
    kitchen_type = models.CharField(max_length=100, blank=True)
    balcony = models.CharField(max_length=100, blank=True)
    elevator = models.BooleanField(null=True, blank=True)
    parking_area = models.CharField(max_length=100, blank=True)
    furnished = models.BooleanField(null=True, blank=True)
    usage_status = models.CharField(max_length=100, blank=True)
    in_complex = models.BooleanField(null=True, blank=True)
    complex_name = models.CharField(max_length=150, blank=True)
    maintenance_fee = models.IntegerField(null=True, blank=True)
    deposit = models.IntegerField(null=True, blank=True)
    deed_status = models.CharField(max_length=100, blank=True)
    from_whom = models.CharField(max_length=100, blank=True)
    is_published = models.BooleanField(default=True)
    list_date = models.DateTimeField(default=datetime.now, blank=True)

    def geocode_address(self):
        """Geocode the address using Nominatim. Skips if coordinates already set."""
        # If we already have coordinates, don't overwrite them
        if self.latitude is not None and self.longitude is not None:
            return
        if not any([self.address, self.city, self.state]):
            return
            
        # Construct the full address
        address_parts = [
            self.address,
            self.city,
            self.state,
            self.zipcode
        ]
        full_address = ", ".join(filter(None, address_parts))
        
        try:
            geolocator = Nominatim(user_agent="coralcity_property")
            location = geolocator.geocode(full_address)
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
                # Don't save here - it will be saved in save() method
        except (GeocoderTimedOut, GeocoderServiceError):
            # If geocoding fails, we'll just leave coordinates as they are
            pass

    def save(self, *args, **kwargs):
        # Allow callers to skip geocoding (used by importers or deferred workflows)
        skip_geocode = kwargs.pop("skip_geocode", False)
        # Only geocode when we don't already have coordinates and the address changed/adding
        should_geocode = False
        if self.latitude is None or self.longitude is None:
            if self._state.adding:
                should_geocode = True
            elif getattr(self, '_address_changed', False):
                should_geocode = True
        if should_geocode and not skip_geocode:
            self.geocode_address()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


def listing_image_upload_to(instance, filename):
    listing = getattr(instance, 'listing', None)
    # Use external_id if present; otherwise fallback to DB pk
    folder_key = None
    if listing is not None:
        folder_key = listing.external_id or (str(listing.pk) if listing.pk else None)
    folder_key = folder_key or 'unknown'
    # Keep original filename base to avoid collisions per listing
    name, ext = os.path.splitext(filename)
    safe_name = (name or 'image').replace('/', '_').replace('\\', '_')
    return f"photos/listing_{folder_key}/{safe_name}{ext or '.jpg'}"


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=listing_image_upload_to, blank=True)
    title = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Optional manual crop box (pixels) applied on save if set
    crop_x = models.PositiveIntegerField(null=True, blank=True)
    crop_y = models.PositiveIntegerField(null=True, blank=True)
    crop_width = models.PositiveIntegerField(null=True, blank=True)
    crop_height = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"Image for {self.listing_id} - {self.title or 'Untitled'}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ListingImage.objects.filter(listing=self.listing, is_primary=True).exclude(
                pk=self.pk
            ).update(is_primary=False)

        # If a crop is requested, attempt to crop using Pillow before saving
        did_crop = False
        try:
            if self.image and all([
                self.crop_x is not None,
                self.crop_y is not None,
                self.crop_width is not None,
                self.crop_height is not None,
            ]):
                from PIL import Image
                import os
                img_path = self.image.path
                with Image.open(img_path) as im:
                    x = int(self.crop_x or 0)
                    y = int(self.crop_y or 0)
                    w = int(self.crop_width or 0)
                    h = int(self.crop_height or 0)
                    if w > 0 and h > 0:
                        # Clamp crop box within image bounds
                        W, H = im.size
                        x = max(0, min(x, W - 1))
                        y = max(0, min(y, H - 1))
                        w = max(1, min(w, W - x))
                        h = max(1, min(h, H - y))
                        box = (x, y, x + w, y + h)
                        im_cropped = im.crop(box)
                        # Overwrite original file
                        im_cropped.save(img_path)
                        did_crop = True
        except Exception:
            pass

        # Clear crop fields after successful crop to avoid re-cropping on next save
        if did_crop:
            self.crop_x = self.crop_y = self.crop_width = self.crop_height = None

        super().save(*args, **kwargs)


    # Convenience property to filter visible images from templates via listing.visible_images
    @property
    def is_croppable(self):
        return all([
            self.crop_x is not None,
            self.crop_y is not None,
            self.crop_width is not None,
            self.crop_height is not None,
        ])


def _listing_visible_images(self):
    return self.images.filter(is_visible=True).order_by('order', 'id')

Listing.visible_images = property(_listing_visible_images)
