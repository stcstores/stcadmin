# Generated by Django 4.0.6 on 2022-07-06 13:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_alter_productimagelink_options_productimage_hash_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productimagelink',
            unique_together={('product', 'image'), ('product', 'position')},
        ),
        migrations.AddField(
            model_name='productimagelink',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='productimagelink',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='hash',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True, unique=True),
        ),
    ]
