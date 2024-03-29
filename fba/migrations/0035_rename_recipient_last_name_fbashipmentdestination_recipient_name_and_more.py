# Generated by Django 4.1.3 on 2022-11-22 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0034_alter_fbaregion_options_fbaregion_position"),
    ]

    operations = [
        migrations.RenameField(
            model_name="fbashipmentdestination",
            old_name="recipient_last_name",
            new_name="recipient_name",
        ),
        migrations.AddField(
            model_name="fbashipmentdestination",
            name="contact_telephone",
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="fbashipmentdestination",
            name="country_iso",
            field=models.CharField(max_length=2, null=True),
        ),
    ]
