# Generated by Django 2.0.7 on 2018-07-31 12:48

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('profit_loss', '0001_initial'), ('profit_loss', '0002_auto_20180125_1155'), ('profit_loss', '0003_auto_20180125_1221'), ('profit_loss', '0004_order_postage_price'), ('profit_loss', '0005_order_shipping_service'), ('profit_loss', '0006_order_customer_id'), ('profit_loss', '0007_auto_20180131_1606'), ('profit_loss', '0008_product'), ('profit_loss', '0009_auto_20180514_0933')]

    dependencies = [
        ('spring_manifest', '0025_auto_20180122_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.PositiveIntegerField(unique=True)),
                ('weight', models.PositiveIntegerField()),
                ('vat_rate', models.PositiveIntegerField(blank=True, null=True)),
                ('price', models.PositiveIntegerField()),
                ('purchase_price', models.PositiveIntegerField()),
                ('item_count', models.PositiveIntegerField()),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='spring_manifest.CloudCommerceCountryID')),
                ('date_recieved', models.DateTimeField(default=django.utils.timezone.now)),
                ('dispatch_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('postage_price', models.PositiveIntegerField(default=0)),
                ('shipping_service', models.CharField(default='none', max_length=250)),
                ('customer_id', models.PositiveIntegerField(default=0)),
                ('department', models.CharField(default='None', max_length=255)),
            ],
            options={
                'ordering': ['-dispatch_date'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=20)),
                ('range_id', models.IntegerField()),
                ('product_id', models.IntegerField()),
                ('name', models.TextField()),
                ('quantity', models.IntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profit_loss.Order')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-dispatch_date'], 'verbose_name': 'Order', 'verbose_name_plural': 'Orders'},
        ),
    ]
