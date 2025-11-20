from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0004_alter_listingimage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='listingimage',
            name='is_visible',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='listingimage',
            name='crop_x',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listingimage',
            name='crop_y',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listingimage',
            name='crop_width',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listingimage',
            name='crop_height',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]

