# Generated by Django 2.0.7 on 2018-07-26 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spring_manifest', '0036_move_services'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='springorder',
            name='service',
        ),
    ]
