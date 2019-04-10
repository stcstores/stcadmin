# Generated by Django 2.2 on 2019-04-10 13:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("inventory", "0037_productrangeselectedoptions_variation")]

    operations = [
        migrations.RenameModel(
            old_name="ProductRangeSelectedOptions",
            new_name="ProductRangeSelectedOption",
        ),
        migrations.AlterModelOptions(
            name="productrangeselectedoption",
            options={
                "ordering": ("product_option",),
                "verbose_name": "ProductRangeSelectedOption",
                "verbose_name_plural": "ProductRangeSelectedOptions",
            },
        ),
    ]
