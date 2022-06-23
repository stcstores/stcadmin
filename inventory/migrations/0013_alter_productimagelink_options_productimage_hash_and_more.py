# Generated by Django 4.0.5 on 2022-06-23 14:07

from django.db import migrations, models
import imagekit.models.fields
import stcadmin.settings


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_remove_productimage_active_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productimagelink',
            options={'ordering': ('position',), 'verbose_name': 'Product Image Link', 'verbose_name_plural': 'Product Image Links'},
        ),
        migrations.AddField(
            model_name='productimage',
            name='hash',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image_file',
            field=imagekit.models.fields.ProcessedImageField(storage=stcadmin.settings.ProductImageStorage, upload_to=''),
        ),
        migrations.AlterUniqueTogether(
            name='productimagelink',
            unique_together={('product', 'image')},
        ),
    ]
