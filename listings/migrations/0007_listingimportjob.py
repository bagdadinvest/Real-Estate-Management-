from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0006_listing_original_url'),
        ('realtors', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ListingImportJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('single_url', models.URLField(blank=True)),
                ('csv_file', models.FileField(blank=True, upload_to='admin_imports/')),
                ('cookie_file', models.FileField(blank=True, upload_to='admin_imports/')),
                ('delay', models.FloatField(default=2.0)),
                ('debug', models.BooleanField(default=False)),
                ('skip_geocode', models.BooleanField(default=False)),
                ('headed', models.BooleanField(default=False)),
                ('no_images', models.BooleanField(default=False)),
                ('images_max', models.PositiveIntegerField(default=15)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('success', 'Success'), ('failed', 'Failed')], db_index=True, default='pending', max_length=16)),
                ('log', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('csv_path_cached', models.CharField(blank=True, max_length=500)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='listing_import_jobs', to=settings.AUTH_USER_MODEL)),
                ('realtor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='import_jobs', to='realtors.realtor')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

