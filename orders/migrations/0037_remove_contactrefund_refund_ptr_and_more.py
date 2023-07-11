# Generated by Django 4.2.3 on 2023-07-11 11:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0036_orderexportdownload"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="contactrefund",
            name="refund_ptr",
        ),
        migrations.RemoveField(
            model_name="courierrefund",
            name="contactrefund_ptr",
        ),
        migrations.RemoveField(
            model_name="courierrefund",
            name="courier",
        ),
        migrations.RemoveField(
            model_name="demicrefund",
            name="supplierrefund_ptr",
        ),
        migrations.RemoveField(
            model_name="linkingmistakerefund",
            name="refund_ptr",
        ),
        migrations.RemoveField(
            model_name="lostinpostrefund",
            name="courierrefund_ptr",
        ),
        migrations.RemoveField(
            model_name="packingmistakerefund",
            name="refund_ptr",
        ),
        migrations.RemoveField(
            model_name="productrefund",
            name="product",
        ),
        migrations.RemoveField(
            model_name="productrefund",
            name="refund",
        ),
        migrations.RemoveField(
            model_name="refund",
            name="order",
        ),
        migrations.RemoveField(
            model_name="refund",
            name="polymorphic_ctype",
        ),
        migrations.RemoveField(
            model_name="refundimage",
            name="product_refund",
        ),
        migrations.RemoveField(
            model_name="refundimage",
            name="refund",
        ),
        migrations.RemoveField(
            model_name="supplierrefund",
            name="contactrefund_ptr",
        ),
        migrations.RemoveField(
            model_name="supplierrefund",
            name="supplier",
        ),
        migrations.DeleteModel(
            name="BreakageRefund",
        ),
        migrations.DeleteModel(
            name="ContactRefund",
        ),
        migrations.DeleteModel(
            name="CourierRefund",
        ),
        migrations.DeleteModel(
            name="DemicRefund",
        ),
        migrations.DeleteModel(
            name="LinkingMistakeRefund",
        ),
        migrations.DeleteModel(
            name="LostInPostRefund",
        ),
        migrations.DeleteModel(
            name="PackingMistakeRefund",
        ),
        migrations.DeleteModel(
            name="ProductRefund",
        ),
        migrations.DeleteModel(
            name="Refund",
        ),
        migrations.DeleteModel(
            name="RefundImage",
        ),
        migrations.DeleteModel(
            name="SupplierRefund",
        ),
    ]
