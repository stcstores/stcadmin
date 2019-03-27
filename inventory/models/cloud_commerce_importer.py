"""Tools to import Products from Cloud Commerce to the database."""

import datetime
from collections import namedtuple

from ccapi import CCAPI
from django.core.exceptions import ValidationError
from django.db import transaction

from . import product_options
from .locations import Bay
from .products import Product, ProductRange
from .suppliers import Supplier
from .vat_rates import VATRate

OptionValue = namedtuple("OptionValue", "ID value")


class ProductImporter:
    """Add Cloud Commerce Products to the database."""

    @classmethod
    @transaction.atomic
    def create(cls, product_ID):
        """Create a new Product from an existing one in Cloud Commerce."""
        cls._check_new(product_ID)
        product = CCAPI.get_product(product_ID)
        new_product = cls._create_product(product)
        new_product.bays.set(cls._get_bays(product))
        cls._set_date_created(product, new_product)
        new_product.status = new_product.COMPLETE
        new_product.save()
        return new_product

    @classmethod
    def _get_option_value(cls, product, option_name):
        value = product.options[option_name].value
        if value is None:
            return OptionValue(None, None)
        return OptionValue(value.id, value.value)

    @classmethod
    def _get_product_option_object(cls, product, model):
        option_value = cls._get_option_value(product, model.PRODUCT_OPTION_NAME)
        return model.objects.get(product_option_value_ID=option_value.ID)

    @classmethod
    def _get_VAT_rate(cls, product):
        return VATRate.objects.get(VAT_rate_ID=product.vat_rate_id)

    @classmethod
    def _check_new(self, product_ID):
        if Product.objects.filter(product_ID=product_ID).exists():
            raise ValidationError("Product already exists.")

    @classmethod
    def _get_range(cls, product):
        return ProductRange.objects.get(range_ID=product.range_id)

    @classmethod
    def _get_bays(cls, product):
        bay_IDs = [_.id for _ in product.bays]
        return Bay.objects.filter(bay_ID__in=bay_IDs)

    @classmethod
    def _get_date_created(cls, product):
        option_value = cls._get_option_value(product, "Date Created").value
        year, month, day = option_value.split("-")
        return datetime.datetime(year=int(year), month=int(month), day=int(day))

    @classmethod
    def _set_date_created(cls, product, new_product):
        new_product.date_created = cls._get_date_created(product)
        new_product.save()

    @classmethod
    def _get_amazon_list(cls, product, option_name):
        if option_name in product.options:
            return cls._get_option_value(product, option_name).value
        return ""

    @classmethod
    def _create_product(cls, product):
        new_product = Product(
            product_ID=product.id,
            product_range=cls._get_range(product),
            SKU=product.sku,
            name=product.name,
            supplier=cls._get_product_option_object(product, Supplier),
            supplier_SKU=cls._get_option_value(product, "Supplier SKU").value,
            barcode=product.barcode,
            purchase_price=cls._get_option_value(product, "Purchase Price").value,
            VAT_rate=cls._get_VAT_rate(product),
            price=product.base_price,
            retail_price=cls._get_option_value(product, "Retail Price").value,
            brand=cls._get_product_option_object(product, product_options.Brand),
            manufacturer=cls._get_product_option_object(
                product, product_options.Manufacturer
            ),
            description=product.description,
            package_type=cls._get_product_option_object(
                product, product_options.PackageType
            ),
            international_shipping=cls._get_product_option_object(
                product, product_options.InternationalShipping
            ),
            weight_grams=int(product.weight),
            length_mm=int(cls._get_option_value(product, "Length MM").value),
            height_mm=int(cls._get_option_value(product, "Height MM").value),
            width_mm=int(cls._get_option_value(product, "Width MM").value),
            multipack=bool(product.product_type),
            amazon_search_terms=cls._get_amazon_list(product, "Amazon Search Terms"),
            amazon_bullet_points=cls._get_amazon_list(product, "Amazon Bullets"),
            status=Product.CREATING,
        )
        new_product.save()
        return new_product

        @classmethod
        def _get_option_value_object(cls, *, product_option, value):
            return product_options.ProductOptionValue.objects.get(
                product_option=product_option, product_option_value_ID=value.ID
            )

        @classmethod
        def _set_product_options(cls, product, new_product):
            cls._check_variable_product_options(product, new_product)
            option_names = set(product.options.option_names.keys())
            options = product_options.ProductOption.objects.filter(
                name__in=option_names
            )
            options_to_set = []
            for product_option in options:
                value = cls._get_option_value(product, product_option.name)
                options_to_set.append(
                    cls._get_option_value_object(product_option, value)
                )
            new_product.product_options.set(options_to_set)

        @classmethod
        def _check_variable_product_options(cls, product, new_product):
            variable_option_names = set(
                _.name for _ in new_product.product_range.variable_options.all()
            )
            options_set_for_product = set(product.options.option_names.keys())
            if not variable_option_names.issubset(options_set_for_product):
                raise Exception(
                    f'Product "{product.sku}" is missing values for variable product '
                    "options."
                )


class ProductRangeImporter:
    """Create a Cloud Commerce Product Range in the database."""

    @classmethod
    @transaction.atomic
    def create(cls, range_ID):
        """Create a Cloud Commerce Product Range in the database."""
        cls._check_new(range_ID)
        product_range = CCAPI.get_range(range_ID)
        new_range = cls._create_range(product_range)
        cls._set_variable_options(product_range, new_range)
        return new_range

    @classmethod
    def _check_new(cls, range_ID):
        if ProductRange.objects.filter(range_ID=range_ID).exists():
            raise ValidationError("Product Range already exists.")

    @classmethod
    def _get_deparment(cls, product_range):
        product = product_range.products[0]
        option_value = product.options[product_options.Department.PRODUCT_OPTION_NAME]
        department_ID = option_value.value.id
        return product_options.Department.objects.get(
            product_option_value_ID=department_ID
        )

    @classmethod
    def _create_range(cls, product_range):
        new_range = ProductRange(
            range_ID=product_range.id,
            SKU=product_range.sku,
            name=product_range.name,
            department=cls._get_deparment(product_range),
            end_of_line=product_range.end_of_line,
        )
        new_range.save()
        return new_range

    @classmethod
    def _set_variable_options(cls, product_range, new_range):
        variation_options_IDs = [
            _.id for _ in product_range.options if _.is_web_shop_select
        ]
        options_to_set = product_options.ProductOption.objects.filter(
            product_option_ID__in=variation_options_IDs
        )
        new_range.save()
        new_range.set_variable_options(options_to_set)
        return new_range


def import_product_from_cloud_commerce(product_ID):
    """Create a new Product from an existing one in Cloud Commerce."""
    return ProductImporter.create(product_ID)


def import_product_range_from_cloud_commerce(range_ID):
    """Create a new Product from an existing one in Cloud Commerce."""
    return ProductRangeImporter.create(range_ID)
