# Generated by Django 2.0.7 on 2018-08-01 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("spring_manifest", "0001_initial_squashed_0055_rename_spring_group")
    ]

    operations = [
        migrations.AlterField(
            model_name="manifestorder",
            name="country",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="spring_manifest.CloudCommerceCountryID",
            ),
        ),
        migrations.AlterField(
            model_name="securedmaildestination",
            name="manifest_row_number",
            field=models.PositiveIntegerField(),
        ),
    ]