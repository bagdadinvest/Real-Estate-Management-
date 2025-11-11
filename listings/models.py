from django.db import models
from datetime import datetime
from django.utils.timezone import timezone
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

from realtors.models import Realtor

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
    property_type = models.CharField(max_length=10)
    bathrooms = models.IntegerField()
    garage = models.IntegerField(default=0)
    sqft = models.IntegerField()
    lot_size = models.DecimalField(max_digits=5, decimal_places=1)
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_5 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_6 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    is_published = models.BooleanField(default=True)
    list_date = models.DateTimeField(default=datetime.now, blank=True)

    def geocode_address(self):
        """Geocode the address using Nominatim"""
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
        # Check if address-related fields have changed
        if not self.pk or any([
            self._state.adding,
            hasattr(self, '_address_changed') and self._address_changed
        ]):
            self.geocode_address()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title