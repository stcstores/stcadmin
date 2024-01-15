# Generated by Django 4.2.6 on 2023-10-31 12:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("fba", "0055_alter_fbaorder_created_at"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fbashipmentpackage",
            name="fba_order",
        ),
        migrations.AlterField(
            model_name="fbashipmentdestination",
            name="contact_telephone",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="fbashipmentexport",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="fbashipmentitem",
            name="quantity",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="fbashipmentitem",
            name="value",
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.AlterField(
            model_name="fbashipmentpackage",
            name="height_cm",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="fbashipmentpackage",
            name="length_cm",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="fbashipmentpackage",
            name="width_cm",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="fbashippingprice",
            name="added",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]