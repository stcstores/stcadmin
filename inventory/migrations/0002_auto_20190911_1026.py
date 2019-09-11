# Generated by Django 2.2.5 on 2019-09-11 10:26

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="barcode", name="used"),
        migrations.AddField(
            model_name="barcode",
            name="added_on",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="barcode",
            name="available",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="barcode",
            name="used_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="barcode", name="used_for", field=models.TextField(null=True)
        ),
        migrations.AddField(
            model_name="barcode", name="used_on", field=models.DateTimeField(null=True)
        ),
    ]
