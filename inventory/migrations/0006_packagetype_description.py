# Generated by Django 3.1.3 on 2020-11-16 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0005_delete_stcadminimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="packagetype",
            name="description",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
