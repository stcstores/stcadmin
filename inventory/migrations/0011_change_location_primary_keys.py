# Generated by Django 2.1.7 on 2019-02-26 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stock_check", "0008_auto_20190226_1200"),
        ("inventory", "0010_remove_bay_FK"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bay", name="bay_id", field=models.PositiveIntegerField()
        ),
        migrations.AlterField(
            model_name="warehouse",
            name="warehouse_id",
            field=models.PositiveIntegerField(),
        ),
        migrations.AddField(
            model_name="bay",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="warehouse",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]