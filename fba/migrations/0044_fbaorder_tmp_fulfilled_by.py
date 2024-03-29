# Generated by Django 4.2.5 on 2023-09-11 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0010_alter_staff_options"),
        ("fba", "0043_alter_fbashipmentitem_country_of_origin_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="fbaorder",
            name="tmp_fulfilled_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fulfilled_fba_orders",
                to="home.staff",
            ),
        ),
    ]
