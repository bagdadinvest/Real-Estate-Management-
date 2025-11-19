from django import forms
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point

from .models import Listing


class MultipleFileInput(forms.ClearableFileInput):
    # Enable HTML multiple uploads in a ClearableFileInput
    allow_multiple_selected = True


class ListingAdminForm(forms.ModelForm):
    """
    Admin form that uses only coordinates (lat/lon) for location entry.
    Also supports bulk image uploads for gallery images.
    """

    latitude = forms.FloatField(
        required=True,
        help_text="Latitude in decimal degrees (e.g. 41.0082)",
        widget=forms.NumberInput(attrs={"step": "any"}),
        label="Latitude",
    )
    longitude = forms.FloatField(
        required=True,
        help_text="Longitude in decimal degrees (e.g. 28.9784)",
        widget=forms.NumberInput(attrs={"step": "any"}),
        label="Longitude",
    )

    bulk_images = forms.FileField(
        required=False,
        widget=MultipleFileInput(),
        help_text="Select multiple files to add them to the gallery.",
        label="Bulk Gallery Images",
    )

    class Meta:
        model = Listing
        fields = [
            "title",
            "price",
            "size_sqm",
            "image",  # primary image
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Do not expose/require the PointField in this form
        # Pre-fill lat/lng if the instance already has a location
        if self.instance and getattr(self.instance, "location", None):
            try:
                self.fields["latitude"].initial = self.instance.location.y
                self.fields["longitude"].initial = self.instance.location.x
            except Exception:
                pass

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lng = cleaned.get("longitude")

        if lat is None or lng is None:
            raise ValidationError("Please provide both latitude and longitude.")
        if not (-90 <= lat <= 90):
            raise ValidationError("Latitude must be between -90 and 90.")
        if not (-180 <= lng <= 180):
            raise ValidationError("Longitude must be between -180 and 180.")

        # Stash computed Point on the form for the admin to use in save_model
        self.computed_point = Point(lng, lat, srid=4326)

        return cleaned
