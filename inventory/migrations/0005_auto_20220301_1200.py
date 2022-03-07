# Generated by Django 3.1.14 on 2022-03-01 12:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inventory", "0004_auto_20220301_1107"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="status",
        ),
        migrations.AddField(
            model_name="productrange",
            name="managed_by",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.PROTECT, to="auth.user"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="productrange",
            name="status",
            field=models.CharField(
                choices=[
                    ("complete", "Complete"),
                    ("creating", "Creating"),
                    ("error", "Error"),
                ],
                default="creating",
                max_length=20,
            ),
        ),
    ]
