# Generated by Django 4.0.4 on 2022-05-19 13:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0028_rename_channel_order_id_order_external_reference_and_more'),
        ('shipping', '0021_region_flag_if_not_delivered_by_days'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courier',
            name='courier_type',
        ),
        migrations.RemoveField(
            model_name='courierservice',
            name='courier',
        ),
        migrations.RemoveField(
            model_name='couriertype',
            name='provider',
        ),
        migrations.RemoveField(
            model_name='shippingrule',
            name='courier_service',
        ),
        migrations.RemoveField(
            model_name='shippingrule',
            name='shipping_service',
        ),
        migrations.DeleteModel(
            name='VATRate',
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ('name',), 'verbose_name': 'Country', 'verbose_name_plural': 'Countries'},
        ),
        migrations.AlterModelOptions(
            name='provider',
            options={'ordering': ('-active', 'name'), 'verbose_name': 'Provider', 'verbose_name_plural': 'Providers'},
        ),
        migrations.AlterModelOptions(
            name='shippingprice',
            options={'ordering': ('-active', 'shipping_service__name'), 'verbose_name': 'Shipping Price', 'verbose_name_plural': 'Shipping Prices'},
        ),
        migrations.AlterModelOptions(
            name='shippingservice',
            options={'ordering': ('-active', 'name'), 'verbose_name': 'Shipping Service', 'verbose_name_plural': 'Shipping Services'},
        ),
        migrations.RenameField(
            model_name='provider',
            old_name='inactive',
            new_name='active',
        ),
        migrations.RenameField(
            model_name='shippingprice',
            old_name='inactive',
            new_name='active',
        ),
        migrations.RemoveField(
            model_name='country',
            name='country_ID',
        ),
        migrations.AddField(
            model_name='shippingservice',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='shippingservice',
            name='full_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shippingservice',
            name='priority',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='shippingservice',
            name='provider',
            field=models.ForeignKey(blank=True, limit_choices_to={'active': True}, null=True, on_delete=django.db.models.deletion.PROTECT, to='shipping.provider'),
        ),
        migrations.AlterField(
            model_name='shippingprice',
            name='shipping_service',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.CASCADE, to='shipping.shippingservice'),
        ),
        migrations.AlterField(
            model_name='shippingservice',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.DeleteModel(
            name='Courier',
        ),
        migrations.DeleteModel(
            name='CourierService',
        ),
        migrations.DeleteModel(
            name='CourierType',
        ),
        migrations.DeleteModel(
            name='ShippingRule',
        ),
    ]
