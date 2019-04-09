# Generated by Django 2.2 on 2019-04-09 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("inventory", "0029_auto_20190409_1409")]

    operations = [
        migrations.AddField(
            model_name="productrange",
            name="variation_options",
            field=models.ManyToManyField(
                blank=True,
                through="inventory.ProductRangeVariableOptions",
                to="inventory.ProductOption",
            ),
        )
    ]
