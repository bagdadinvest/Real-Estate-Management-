"""
Management command to pre-compute and cache closest stores for all listings.
This should be run after adding new listings or when configuration changes.
"""
import logging
from django.core.management.base import BaseCommand
from listings.models import DisplayConfig
from listings.services import ClosestStoresService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Pre-compute and cache the closest stores for all listings"
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--invalidate",
            action="store_true",
            help="Invalidate all existing cache before recomputing",
        )
        parser.add_argument(
            "--invalidate-only",
            action="store_true",
            help="Only invalidate cache, don't recompute",
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        self.stdout.write(self.style.HTTP_INFO("Closest Stores Cache Management"))
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        
        # Show current configuration
        config = DisplayConfig.get_config()
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Configuration loaded:\n"
            f"  - Closest grocery stores per listing: {config.closest_grocery_stores}\n"
            f"  - Closest clothing stores per listing: {config.closest_clothing_stores}"
        ))
        
        if options["invalidate_only"]:
            self.stdout.write(self.style.WARNING("\n⚠ Invalidating all cache..."))
            ClosestStoresService.invalidate_all_cache()
            self.stdout.write(self.style.SUCCESS("✓ Cache invalidated!"))
            return
        
        if options["invalidate"]:
            self.stdout.write(self.style.WARNING("\n⚠ Invalidating all cache..."))
            ClosestStoresService.invalidate_all_cache()
            self.stdout.write(self.style.SUCCESS("✓ Cache invalidated!"))
        
        self.stdout.write(self.style.HTTP_INFO("\n⏳ Computing cache for all listings..."))
        stats = ClosestStoresService.compute_all_listings()
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Cache computation complete!\n"
            f"  - Total listings: {stats['total']}\n"
            f"  - Successful: {stats['successful']}\n"
            f"  - Failed: {stats['failed']}\n"
            f"  - Elapsed time: {stats['elapsed_seconds']:.2f}s"
        ))
        
        if stats["errors"]:
            self.stdout.write(self.style.ERROR(
                f"\n⚠ Errors encountered:\n"
                f"{chr(10).join('  - ' + e for e in stats['errors'])}"
            ))
        
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
