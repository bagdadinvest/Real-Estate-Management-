import os
import shutil
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = (
        "Build a deployable static site into DISTILL_DIR including HTML (django-distill), "
        "collected static files, and copied media uploads."
    )

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', help='Clean DISTILL_DIR before building')
        parser.add_argument('--skip-html', action='store_true', help='Skip distilling HTML pages')
        parser.add_argument('--skip-static', action='store_true', help='Skip collecting static files')
        parser.add_argument('--skip-media', action='store_true', help='Skip copying media uploads')

    def handle(self, *args, **opts):
        distill_dir = getattr(settings, 'DISTILL_DIR', None)
        if not distill_dir:
            raise SystemExit('DISTILL_DIR is not configured in settings.')

        if opts['clean'] and os.path.isdir(distill_dir):
            self.stdout.write(f"Cleaning {distill_dir} ...")
            shutil.rmtree(distill_dir)

        os.makedirs(distill_dir, exist_ok=True)

        # 1) HTML: run django-distill to emit static pages
        if not opts.get('skip_html'):
            self.stdout.write("[1/3] Generating HTML with django-distill")
            # Ensure language-specific output uses the configured patterns
            # django-distill registers the command as 'distill-local'
            call_command('distill-local')
        else:
            self.stdout.write("[1/3] Skipped HTML generation")

        # 2) Static: collect all static assets into DISTILL_DIR/static
        if not opts.get('skip_static'):
            self.stdout.write("[2/3] Collecting static files")
            dest_static = os.path.join(distill_dir, 'static')
            # Mutate STATIC_ROOT during this run so collectstatic targets distill dir
            try:
                settings.STATIC_ROOT  # ensure exists
            except Exception:
                pass
            settings.STATIC_ROOT = dest_static
            os.environ['COLLECT_STATIC_TO_DISTILL'] = '1'
            # interactive=False (`--noinput`), clear existing files for idempotency
            call_command('collectstatic', interactive=False, clear=True, verbosity=1)
        else:
            self.stdout.write("[2/3] Skipped static collection")

        # 3) Media: copy user uploads into DISTILL_DIR/media
        if not opts.get('skip_media'):
            self.stdout.write("[3/3] Copying media uploads")
            call_command('copy_media_to_distill', clean=True)
        else:
            self.stdout.write("[3/3] Skipped media copy")

        self.stdout.write(self.style.SUCCESS("Static site build complete."))
