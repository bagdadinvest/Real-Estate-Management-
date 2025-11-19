"""
Optional: Signals for automatic cache invalidation.
This module provides automatic cache invalidation when stores or listings change.

Usage: Add to listings/apps.py:
    def ready(self):
        import listings.signals
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from stores_layer.models import Grocery, Clothing
from .models import Listing
from .services import ClosestStoresService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Listing)
def invalidate_cache_on_listing_update(sender, instance, created, **kwargs):
    """
    Invalidate cache when a listing is updated.
    For new listings, cache will be computed on first request.
    """
    if not created:  # Only on update, not on create
        logger.info(f"[SIGNAL] Listing {instance.id} updated, invalidating cache")
        ClosestStoresService.invalidate_cache(instance)


@receiver(post_delete, sender=Listing)
def cleanup_cache_on_listing_delete(sender, instance, **kwargs):
    """
    Clean up cache when a listing is deleted.
    (Usually handled by CASCADE, but being explicit)
    """
    logger.info(f"[SIGNAL] Listing {instance.id} deleted")


@receiver(post_save, sender=Grocery)
def invalidate_all_cache_on_grocery_change(sender, instance, created, **kwargs):
    """
    Invalidate all caches when a grocery store is created/updated.
    This ensures all listings reflect the latest store locations.
    """
    action = "created" if created else "updated"
    logger.warning(
        f"[SIGNAL] Grocery store {instance.id} {action}, "
        f"invalidating all caches (expensive operation)"
    )
    ClosestStoresService.invalidate_all_cache()


@receiver(post_delete, sender=Grocery)
def invalidate_all_cache_on_grocery_delete(sender, instance, **kwargs):
    """
    Invalidate all caches when a grocery store is deleted.
    """
    logger.warning(
        f"[SIGNAL] Grocery store {instance.id} deleted, "
        f"invalidating all caches (expensive operation)"
    )
    ClosestStoresService.invalidate_all_cache()


@receiver(post_save, sender=Clothing)
def invalidate_all_cache_on_clothing_change(sender, instance, created, **kwargs):
    """
    Invalidate all caches when a clothing store is created/updated.
    This ensures all listings reflect the latest store locations.
    """
    action = "created" if created else "updated"
    logger.warning(
        f"[SIGNAL] Clothing store {instance.id} {action}, "
        f"invalidating all caches (expensive operation)"
    )
    ClosestStoresService.invalidate_all_cache()


@receiver(post_delete, sender=Clothing)
def invalidate_all_cache_on_clothing_delete(sender, instance, **kwargs):
    """
    Invalidate all caches when a clothing store is deleted.
    """
    logger.warning(
        f"[SIGNAL] Clothing store {instance.id} deleted, "
        f"invalidating all caches (expensive operation)"
    )
    ClosestStoresService.invalidate_all_cache()
