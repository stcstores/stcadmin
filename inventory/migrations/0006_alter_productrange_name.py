# Generated by Django 4.0.3 on 2022-04-05 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_packagetype_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productrange',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
    ]