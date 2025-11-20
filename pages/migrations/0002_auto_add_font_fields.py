from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='themesettings',
            name='font_import_url',
            field=models.CharField(blank=True, default='', help_text='Full Google Fonts <link> href or CSS @import URL', max_length=300),
        ),
        migrations.AddField(
            model_name='themesettings',
            name='font_selectors',
            field=models.CharField(default='html, body', help_text='CSS selectors to apply the font-family to', max_length=300),
        ),
        migrations.AddField(
            model_name='themesettings',
            name='custom_css',
            field=models.TextField(blank=True, default='', help_text='Additional CSS overrides injected after theme variables'),
        ),
    ]

