# Generated by Django 4.2.2 on 2023-06-27 14:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("restock", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="reorder",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
    ]