# Generated by Django 4.0.5 on 2022-06-22 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_alter_supplier_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImageLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='baseproduct',
            name='images',
            field=models.ManyToManyField(related_name='image_products', through='inventory.ProductImageLink', to='inventory.productimage'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='old_images', to='inventory.baseproduct'),
        ),
        migrations.AddField(
            model_name='productimagelink',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_image_links', to='inventory.productimage'),
        ),
        migrations.AddField(
            model_name='productimagelink',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_image_links', to='inventory.baseproduct'),
        ),
    ]
