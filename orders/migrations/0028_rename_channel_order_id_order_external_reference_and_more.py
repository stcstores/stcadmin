# Generated by Django 4.0.4 on 2022-05-19 13:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0021_region_flag_if_not_delivered_by_days'),
        ('orders', '0027_remove_orderdetailsupdateerror_product_sale_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='channel_order_ID',
            new_name='external_reference',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='order_ID',
            new_name='order_id',
        ),
        migrations.RenameField(
            model_name='productsale',
            old_name='vat_rate',
            new_name='vat',
        ),
        migrations.AlterUniqueTogether(
            name='productsale',
            unique_together={('order', 'sku')},
        ),
        migrations.RemoveField(
            model_name='order',
            name='courier_service',
        ),
        migrations.RemoveField(
            model_name='order',
            name='customer_ID',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_rule',
        ),
        migrations.AddField(
            model_name='channel',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_service',
            field=models.ForeignKey(blank=True, limit_choices_to={'active': True}, null=True, on_delete=django.db.models.deletion.PROTECT, to='shipping.shippingservice'),
        ),
        migrations.AddField(
            model_name='productsale',
            name='channel_sku',
            field=models.CharField(max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='channel',
            field=models.ForeignKey(blank=True, limit_choices_to={'active': True}, null=True, on_delete=django.db.models.deletion.PROTECT, to='orders.channel'),
        ),
        migrations.RemoveField(
            model_name='productsale',
            name='details_success',
        ),
        migrations.RemoveField(
            model_name='productsale',
            name='end_of_line',
        ),
        migrations.RemoveField(
            model_name='productsale',
            name='product_ID',
        ),
    ]
