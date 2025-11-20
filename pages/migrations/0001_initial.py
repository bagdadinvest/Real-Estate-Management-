from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ThemeSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_color', models.CharField(default='#c3476c', max_length=16)),
                ('accent_color', models.CharField(default='#0071f8', max_length=16)),
                ('background_color', models.CharField(default='#ffffff', max_length=16)),
                ('text_color', models.CharField(default='#1e1e1e', max_length=16)),
                ('font_family', models.CharField(default='Titillium Web, sans-serif', max_length=200)),
            ],
            options={
                'verbose_name': 'Theme Settings',
                'verbose_name_plural': 'Theme Settings',
            },
        ),
    ]

