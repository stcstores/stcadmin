# Generated by Django 3.1.3 on 2020-11-26 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0014_vatrate"),
    ]

    operations = [
        migrations.AddField(
            model_name="country",
            name="flag",
            field=models.ImageField(blank=True, null=True, upload_to="flags"),
        ),
    ]
