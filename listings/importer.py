import io
import os
import threading
from datetime import datetime
from django.conf import settings
from django.core.management import call_command
from django.db import close_old_connections
from django.utils import timezone

from .models import ListingImportJob


class DBLogStream(io.TextIOBase):
    def __init__(self, job_id: int):
        self.job_id = job_id
        self._buffer = []

    def writable(self):
        return True

    def write(self, s: str):
        if not s:
            return 0
        try:
            # Append to DB incrementally to surface progress
            job = ListingImportJob.objects.filter(id=self.job_id).only('id', 'log').first()
            if job:
                job.log = (job.log or '') + str(s)
                job.save(update_fields=['log'])
        except Exception:
            # Avoid breaking command on logging errors
            pass
        return len(s)


def _ensure_dir(path: str):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)


def _build_csv_for_single_url(job_id: int, url: str) -> str:
    base_dir = os.path.join(settings.MEDIA_ROOT, 'admin_imports')
    os.makedirs(base_dir, exist_ok=True)
    csv_path = os.path.join(base_dir, f'job_{job_id}_links.csv')
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write('url\n')
        f.write(url.strip())
        f.write('\n')
    return csv_path


def _run_job(job_id: int):
    try:
        job = ListingImportJob.objects.select_related('realtor').get(id=job_id)
    except ListingImportJob.DoesNotExist:
        return

    # Mark running
    job.status = 'running'
    job.started_at = timezone.now()
    job.save(update_fields=['status', 'started_at'])

    # Determine csv path
    csv_path = ''
    try:
        if job.csv_file:
            csv_path = job.csv_file.path
        elif job.single_url:
            csv_path = _build_csv_for_single_url(job.id, job.single_url)
        else:
            raise ValueError('Provide either a CSV file or a single URL')
    except Exception as e:
        job.status = 'failed'
        job.finished_at = timezone.now()
        job.log = (job.log or '') + f"\n[admin] Error preparing CSV: {e}\n"
        job.save(update_fields=['status', 'finished_at', 'log'])
        return

    # Cache for audit
    try:
        job.csv_path_cached = csv_path
        job.save(update_fields=['csv_path_cached'])
    except Exception:
        pass

    # Build command options
    opts = {
        'realtor_id': job.realtor_id,
        'delay': float(job.delay or 0) or 0.0,
        'debug': bool(job.debug),
        'skip_geocode': bool(job.skip_geocode),
        'headed': bool(job.headed),
        'no_images': bool(job.no_images),
        'images_max': int(job.images_max or 0) or 15,
    }
    if job.cookie_file:
        try:
            opts['cookie_file'] = job.cookie_file.path
        except Exception:
            pass

    stream = DBLogStream(job_id)

    try:
        # Close old DB connections prior to long-running job
        close_old_connections()
        call_command('import_listings_with_playwright', csv_path, stdout=stream, **opts)
        # Success
        job.status = 'success'
    except Exception as e:
        # Record failure and error
        try:
            stream.write(f"\n[admin] Job failed: {e}\n")
        except Exception:
            pass
        job.status = 'failed'
    finally:
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'finished_at'])
        close_old_connections()


def start_import_job_async(job_id: int):
    t = threading.Thread(target=_run_job, args=(job_id,), name=f"listing-import-job-{job_id}", daemon=True)
    t.start()

