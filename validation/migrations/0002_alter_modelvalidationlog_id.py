# Generated by Django 3.2.3 on 2021-06-01 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("validation", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="modelvalidationlog",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
