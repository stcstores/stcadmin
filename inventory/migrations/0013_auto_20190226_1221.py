# Generated by Django 2.1.7 on 2019-02-26 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("inventory", "0012_re_add_bay_FK")]

    operations = [
        migrations.AlterField(
            model_name="bay",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="warehouse",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
