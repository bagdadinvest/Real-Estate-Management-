from django.contrib.gis.db import models
import logging

logger = logging.getLogger(__name__)


class DisplayConfig(models.Model):
    """
    Singleton model to control how many entries are displayed on the frontend.
    Only one instance should exist.
    """
    max_listings = models.PositiveIntegerField(
        default=100,
        help_text="Maximum number of listings to display (default: 100)"
    )
    # Closest stores per listing to pre-compute and cache
    closest_grocery_stores = models.PositiveIntegerField(
        default=20,
        help_text="Number of closest grocery stores to pre-compute per listing (default: 20)"
    )
    closest_clothing_stores = models.PositiveIntegerField(
        default=20,
        help_text="Number of closest clothing stores to pre-compute per listing (default: 20)"
    )
    # Legacy display counts (for filtering on frontend if needed)
    max_grocery_stores = models.PositiveIntegerField(
        default=200,
        help_text="Maximum number of grocery stores to display (default: 200)"
    )
    max_clothing_stores = models.PositiveIntegerField(
        default=200,
        help_text="Maximum number of clothing stores to display (default: 200)"
    )
    max_metro_stations = models.PositiveIntegerField(
        default=100,
        help_text="Maximum number of metro stations to display (default: 100)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Display Configuration"
        verbose_name_plural = "Display Configuration"

    def __str__(self) -> str:  # pragma: no cover
        return "Display Settings (Singleton)"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        logger.info(
            f"[CONFIG_SAVED] Updated display limits - "
            f"Listings: {self.max_listings}, "
            f"Grocery: {self.max_grocery_stores}, "
            f"Clothing: {self.max_clothing_stores}, "
            f"Metro: {self.max_metro_stations}"
        )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Prevent deletion of singleton
        logger.warning("[CONFIG_DELETE_ATTEMPTED] Deletion of DisplayConfig prevented (singleton protection)")
        pass

    @classmethod
    def get_config(cls):
        """Get or create the singleton configuration instance."""
        config, created = cls.objects.get_or_create(pk=1)
        if created:
            logger.info("[CONFIG_CREATED] New DisplayConfig created with default values")
        else:
            logger.debug(
                f"[CONFIG_RETRIEVED] Current limits - "
                f"Listings: {config.max_listings}, "
                f"Grocery: {config.max_grocery_stores}, "
                f"Clothing: {config.max_clothing_stores}, "
                f"Metro: {config.max_metro_stations}"
            )
        return config



class Listing(models.Model):
    title = models.CharField(max_length=255)
    price = models.BigIntegerField()
    size_sqm = models.PositiveIntegerField()
    # Use geography=True to get meter-based distances directly
    location = models.PointField(srid=4326, geography=True)
    
    # Building image/photo - exterior building photo (primary image)
    image = models.ImageField(upload_to='listings/', null=True, blank=True, help_text="Primary exterior building photo")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} - {self.price} TL"

    def get_primary_image(self):
        """Get the primary image (first uploaded or marked as primary)."""
        primary_image = self.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image
        return self.images.first().image if self.images.exists() else None


class ListingImage(models.Model):
    """
    Model to store multiple images for each listing.
    Allows for gallery functionality and multiple property photos.
    """
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="The listing this image belongs to"
    )
    
    image = models.ImageField(
        upload_to='listings/images/',
        help_text="Property image (interior, exterior, floor plan, etc.)"
    )
    
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional title/description of the image (e.g., 'Living Room', 'Master Bedroom')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Optional longer description of the image"
    )
    
    # Ordering within listing's gallery
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which to display images in the gallery"
    )
    
    # Mark one image as primary/featured
    is_primary = models.BooleanField(
        default=False,
        help_text="Use this image as the primary thumbnail for the listing"
    )
    
    # Image metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.CharField(
        max_length=255,
        blank=True,
        help_text="Username or source of the upload"
    )
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Listing Image"
        verbose_name_plural = "Listing Images"
        indexes = [
            models.Index(fields=['listing', 'order']),
            models.Index(fields=['is_primary']),
        ]
    
    def __str__(self) -> str:  # pragma: no cover
        title = self.title or "Untitled"
        return f"{self.listing.title} - {title}"
    
    def save(self, *args, **kwargs):
        """Ensure only one image per listing is marked as primary."""
        if self.is_primary:
            # Mark all other images for this listing as non-primary
            ListingImage.objects.filter(
                listing=self.listing,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # If this is the first image for the listing, make it primary
        if not ListingImage.objects.filter(listing=self.listing).exists():
            self.is_primary = True
        
        logger.info(
            f"[IMAGE_SAVED] {self.listing.title} - {self.title or 'Untitled'} "
            f"(primary: {self.is_primary}, order: {self.order})"
        )
        super().save(*args, **kwargs)


class ClosestStoresCache(models.Model):
    """
    Cache model to store pre-computed closest stores for each listing.
    This avoids computing distances on every request and improves frontend performance.
    """
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name="closest_stores_cache")
    
    # JSON storage for closest stores with their distances
    # Format: {"grocery": [{"id": 1, "name": "Store A", "distance_m": 500}, ...], "clothing": [...]}
    closest_grocery_ids = models.JSONField(
        default=list,
        help_text="List of closest grocery store IDs ordered by distance"
    )
    closest_clothing_ids = models.JSONField(
        default=list,
        help_text="List of closest clothing store IDs ordered by distance"
    )
    
    # Track when this was last computed
    computed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Closest Stores Cache"
        verbose_name_plural = "Closest Stores Cache"
        indexes = [
            models.Index(fields=['listing']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self) -> str:  # pragma: no cover
        return f"Cache for Listing {self.listing.id}: {len(self.closest_grocery_ids)} grocery, {len(self.closest_clothing_ids)} clothing"

