# Generated by Django 2.0 on 2017-12-13 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spring_manifest', '0023_springmanifest_messages'),
    ]

    operations = [
        migrations.RenameField(
            model_name='springmanifest',
            old_name='messages',
            new_name='errors',
        ),
    ]
