# Generated by Django 4.0.5 on 2022-06-30 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linnworks', '0010_alter_linnworksorder_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='linnworkschannel',
            name='item_link_format',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='linnworkschannel',
            name='readable_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
