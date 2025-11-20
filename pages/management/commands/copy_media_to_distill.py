import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = "Copy MEDIA_ROOT into DISTILL_DIR/media so static site has uploads."

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', help='Remove existing destination before copying')

    def handle(self, *args, **options):
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        distill_dir = getattr(settings, 'DISTILL_DIR', None)
        if not media_root or not os.path.isdir(media_root):
            raise CommandError(f"MEDIA_ROOT not found: {media_root}")
        if not distill_dir:
            raise CommandError("DISTILL_DIR is not configured in settings")
        dest = os.path.join(distill_dir, 'media')
        src = media_root

        self.stdout.write(f"Copying media: {src} -> {dest}")
        if options.get('clean') and os.path.isdir(dest):
            shutil.rmtree(dest)

        os.makedirs(dest, exist_ok=True)

        # Copy tree (files only; preserve subpaths)
        for root, dirs, files in os.walk(src):
            rel = os.path.relpath(root, src)
            target_dir = os.path.join(dest, rel) if rel != '.' else dest
            os.makedirs(target_dir, exist_ok=True)
            for name in files:
                s = os.path.join(root, name)
                d = os.path.join(target_dir, name)
                try:
                    shutil.copy2(s, d)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Skip {s}: {e}"))

        self.stdout.write(self.style.SUCCESS("Media copied."))

