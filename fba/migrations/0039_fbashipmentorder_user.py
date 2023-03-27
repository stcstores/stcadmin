# Generated by Django 4.1.7 on 2023-03-27 12:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("fba", "0038_remove_fbaorder_tracking_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="fbashipmentorder",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fba_shipments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
