# Generated by Django 3.0.8 on 2020-07-22 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("orders", "0012_auto_20200715_1225")]

    operations = [
        migrations.AddField(
            model_name="refund", name="notes", field=models.TextField(blank=True)
        )
    ]
