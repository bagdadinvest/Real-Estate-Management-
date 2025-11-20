from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0005_listingimage_visibility_and_crop'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='original_url',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]

