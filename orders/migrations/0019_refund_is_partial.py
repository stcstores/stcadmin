# Generated by Django 3.1.3 on 2020-11-19 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0018_lostinpostrefund_returned"),
    ]

    operations = [
        migrations.AddField(
            model_name="refund",
            name="is_partial",
            field=models.BooleanField(default=False),
        ),
    ]
