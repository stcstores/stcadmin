# Generated by Django 2.0.2 on 2018-04-18 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spring_manifest', '0027_auto_20180418_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='securedmaildestination',
            name='manifest_row_number',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
