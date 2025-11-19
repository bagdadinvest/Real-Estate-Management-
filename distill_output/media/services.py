"""
Service module for managing closest stores cache.
Handles pre-computation and storage of nearest stores for each listing.
"""
import logging
import time
from typing import List, Dict, Any
from django.contrib.gis.db.models.functions import Distance
from django.db import transaction

from .models import Listing, DisplayConfig, ClosestStoresCache
from stores_layer.models import Grocery, Clothing

logger = logging.getLogger(__name__)


class ClosestStoresService:
    """
    Service class for managing and caching the closest stores for listings.
    """
    
    @staticmethod
    def compute_closest_stores_for_listing(listing: Listing, config: DisplayConfig) -> ClosestStoresCache:
        """
        Compute and cache the closest stores for a given listing.
        
        Args:
            listing: The Listing instance
            config: DisplayConfig with the number of closest stores to compute
            
        Returns:
            ClosestStoresCache: Created or updated cache object
        """
        start_time = time.time()
        
        logger.debug(f"[CACHE_COMPUTE_START] Listing {listing.id} ({listing.title})")
        
        # Get closest grocery stores
        grocery_start = time.time()
        closest_grocery_ids = list(
            Grocery.objects.annotate(distance=Distance("location", listing.location))
            .order_by("distance")
            .values_list("id", flat=True)[: config.closest_grocery_stores]
        )
        grocery_time = time.time() - grocery_start
        logger.debug(
            f"[CACHE_GROCERY] Listing {listing.id}: Found {len(closest_grocery_ids)} stores | Time: {grocery_time:.4f}s"
        )
        
        # Get closest clothing stores
        clothing_start = time.time()
        closest_clothing_ids = list(
            Clothing.objects.annotate(distance=Distance("location", listing.location))
            .order_by("distance")
            .values_list("id", flat=True)[: config.closest_clothing_stores]
        )
        clothing_time = time.time() - clothing_start
        logger.debug(
            f"[CACHE_CLOTHING] Listing {listing.id}: Found {len(closest_clothing_ids)} stores | Time: {clothing_time:.4f}s"
        )
        
        # Save or update cache
        cache, created = ClosestStoresCache.objects.update_or_create(
            listing=listing,
            defaults={
                "closest_grocery_ids": closest_grocery_ids,
                "closest_clothing_ids": closest_clothing_ids,
            }
        )
        
        elapsed = time.time() - start_time
        action = "CREATED" if created else "UPDATED"
        logger.info(
            f"[CACHE_{action}] Listing {listing.id}: "
            f"{len(closest_grocery_ids)} grocery + {len(closest_clothing_ids)} clothing | "
            f"Time: {elapsed:.4f}s"
        )
        
        return cache
    
    @staticmethod
    def compute_all_listings() -> Dict[str, Any]:
        """
        Compute and cache closest stores for all listings.
        
        Returns:
            Dictionary with statistics about the cache computation
        """
        config = DisplayConfig.get_config()
        all_listings = Listing.objects.all()
        total = all_listings.count()
        
        logger.info(f"[CACHE_BATCH_START] Computing cache for {total} listings")
        start_time = time.time()
        
        stats = {
            "total": total,
            "successful": 0,
            "failed": 0,
            "errors": [],
        }
        
        for idx, listing in enumerate(all_listings, 1):
            try:
                ClosestStoresService.compute_closest_stores_for_listing(listing, config)
                stats["successful"] += 1
                
                if idx % 10 == 0:
                    logger.info(f"[CACHE_BATCH_PROGRESS] {idx}/{total} listings processed")
                    
            except Exception as e:
                stats["failed"] += 1
                error_msg = f"Listing {listing.id}: {str(e)}"
                stats["errors"].append(error_msg)
                logger.error(f"[CACHE_COMPUTE_ERROR] {error_msg}", exc_info=True)
        
        elapsed = time.time() - start_time
        logger.info(
            f"[CACHE_BATCH_COMPLETE] "
            f"Successful: {stats['successful']}, Failed: {stats['failed']} | "
            f"Total time: {elapsed:.4f}s"
        )
        
        stats["elapsed_seconds"] = elapsed
        return stats
    
    @staticmethod
    def get_cached_stores(listing: Listing) -> tuple:
        """
        Retrieve cached closest stores for a listing.
        If cache doesn't exist, compute it on the fly.
        
        Args:
            listing: The Listing instance
            
        Returns:
            Tuple of (closest_grocery_ids, closest_clothing_ids)
        """
        try:
            cache = listing.closest_stores_cache
            logger.debug(
                f"[CACHE_HIT] Listing {listing.id}: "
                f"Retrieved {len(cache.closest_grocery_ids)} grocery, {len(cache.closest_clothing_ids)} clothing"
            )
            return cache.closest_grocery_ids, cache.closest_clothing_ids
        except ClosestStoresCache.DoesNotExist:
            logger.warning(f"[CACHE_MISS] Listing {listing.id}: Computing on-the-fly")
            config = DisplayConfig.get_config()
            cache = ClosestStoresService.compute_closest_stores_for_listing(listing, config)
            return cache.closest_grocery_ids, cache.closest_clothing_ids
    
    @staticmethod
    def invalidate_cache(listing: Listing) -> None:
        """
        Invalidate cache for a specific listing.
        
        Args:
            listing: The Listing instance
        """
        try:
            listing.closest_stores_cache.delete()
            logger.info(f"[CACHE_INVALIDATED] Listing {listing.id}")
        except ClosestStoresCache.DoesNotExist:
            logger.debug(f"[CACHE_NOT_FOUND] Listing {listing.id}: Nothing to invalidate")
    
    @staticmethod
    def invalidate_all_cache() -> None:
        """
        Invalidate all cached closest stores.
        """
        count = ClosestStoresCache.objects.all().delete()[0]
        logger.info(f"[CACHE_INVALIDATED_ALL] Deleted {count} cache entries")
