# Generated by Django 4.0.6 on 2022-07-06 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linnworks', '0012_linnworksconfig_last_image_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='linnworksconfig',
            name='image_import_file_path',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
