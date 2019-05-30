"""Tools to import Products from Cloud Commerce to the database."""

import datetime
from collections import namedtuple

from ccapi import CCAPI
from django.core.exceptions import ValidationError
from django.db import transaction

from . import product_options, products
from .locations import Bay
from .product_image import ProductImage
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
        cls._set_product_options(product, new_product)
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
        if products.Product.objects.filter(product_ID=product_ID).exists():
            raise ValidationError("Product already exists.")

    @classmethod
    def _get_range(cls, product):
        return products.ProductRange.objects.get(range_ID=product.range_id)

    @classmethod
    def _get_bays(cls, product):
        bay_IDs = [_.id for _ in product.bays or []]
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
    def _create_product(cls, product):
        new_product = products.Product(
            product_ID=product.id,
            product_range=cls._get_range(product),
            SKU=product.sku,
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
            status=products.Product.CREATING,
        )
        new_product.save()
        return new_product

    @classmethod
    def _get_option_value_object(cls, *, product_option, value):
        try:
            return product_options.ProductOptionValue.objects.get(
                product_option=product_option, product_option_value_ID=value.ID
            )
        except product_options.ProductOptionValue.DoesNotExist:
            raise Exception(
                (
                    f'Product option value "{value.value}" does not exist for product '
                    f'option "{product_option.name}".'
                )
            )

    @classmethod
    def _set_product_options(cls, product, new_product):
        cls._check_variable_product_options(product, new_product)
        option_names = set(product.options.option_names.keys())
        options = product_options.ProductOption.objects.filter(name__in=option_names)
        options_to_set = []
        for product_option in options:
            value = cls._get_option_value(product, product_option.name)
            options_to_set.append(
                cls._get_option_value_object(product_option=product_option, value=value)
            )
        new_product.product_options.set(options_to_set)

    @classmethod
    def _check_variable_product_options(cls, product, new_product):
        variable_option_names = set(
            _.name for _ in new_product.product_range.variation_options()
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
        cls._set_product_options(product_range, new_range)
        cls._create_products(product_range)
        return new_range

    @classmethod
    def _create_products(cls, product_range):
        """Create the range's products in the database."""
        product_IDs = [_.id for _ in product_range.products]
        for product_ID in product_IDs:
            ProductImporter.create(product_ID)

    @classmethod
    def _check_new(cls, range_ID):
        if products.ProductRange.objects.filter(range_ID=range_ID).exists():
            raise ValidationError("Product Range already exists.")

    @classmethod
    def _get_amazon_search_terms(cls, product_range):
        product = product_range.products[0]
        option_value = product.options[product_options.Department.PRODUCT_OPTION_NAME]
        department_ID = option_value.value.id
        return product_options.Department.objects.get(
            product_option_value_ID=department_ID
        )

    @classmethod
    def _get_deparment(cls, product):
        option_value = product.options[product_options.Department.PRODUCT_OPTION_NAME]
        department_ID = option_value.value.id
        return product_options.Department.objects.get(
            product_option_value_ID=department_ID
        )

    @classmethod
    def _get_amazon_list(cls, product, option_name):
        if option_name in product.options:
            return cls._get_option_value(product, option_name).value
        return ""

    @classmethod
    def _create_range(cls, product_range):
        product = product_range.products[0]
        new_range = products.ProductRange(
            range_ID=product_range.id,
            SKU=product_range.sku,
            name=product_range.name,
            department=cls._get_deparment(product),
            description=product.description or "",
            amazon_search_terms=cls._get_amazon_list(product, "Amazon Search Terms"),
            amazon_bullet_points=cls._get_amazon_list(product, "Amazon Bullets"),
            end_of_line=product_range.end_of_line,
        )
        new_range.save()
        return new_range

    @classmethod
    def _set_product_options(cls, product_range, new_range):
        variation_options_IDs = []
        listing_option_IDs = []
        for option in product_range.options:
            if option.is_web_shop_select:
                variation_options_IDs.append(option.id)
            else:
                listing_option_IDs.append(option.id)
        variation_options = product_options.ProductOption.objects.filter(
            product_option_ID__in=variation_options_IDs
        )
        listing_options = product_options.ProductOption.objects.filter(
            product_option_ID__in=listing_option_IDs
        )
        options_to_create = []
        for option in variation_options:
            selected_option = products.ProductRangeSelectedOption(
                product_range=new_range, product_option=option, variation=True
            )
            options_to_create.append(selected_option)
        for option in listing_options:
            selected_option = products.ProductRangeSelectedOption(
                product_range=new_range, product_option=option, variation=False
            )
            options_to_create.append(selected_option)
        products.ProductRangeSelectedOption.objects.bulk_create(options_to_create)
        return new_range


class ProductImageImporter:
    """Add product images to the database."""

    @classmethod
    @transaction.atomic
    def create(cls, product):
        """Add product images to the database."""
        images = CCAPI.get_product_images(
            product.product_range.range_ID, product.product_ID
        )
        for position, CC_image in enumerate(images):
            cls.add_image(product=product, CC_image=CC_image, position=position)

    @classmethod
    def add_image(cls, product, CC_image, position):
        """Add an image to the database."""
        image, created = ProductImage.objects.get_or_create(
            image_ID=CC_image.id,
            defaults={
                "product": product,
                "filename": CC_image.filename,
                "URL": CC_image.url,
                "position": position,
            },
        )
        if not created:
            image.product = product
            image.filename = CC_image.filename
            image.URL = CC_image.url
            image.position = position
            image.save()


def import_product_from_cloud_commerce(product_ID):
    """
    Create a new Product from an existing one in Cloud Commerce.

    Args:
        product_ID (str): The Cloud Commerce product ID for the product.
    """
    return ProductImporter.create(product_ID)


def import_product_range_from_cloud_commerce(range_ID):
    """
    Create a new Product from an existing one in Cloud Commerce.

    Args:
        range_ID (str): The Cloud Commerce range ID for the product range.
    """
    return ProductRangeImporter.create(range_ID)


def import_product_images_from_cloud_commerce(product):
    """
    Add product images to the database.

    Args:
        product: (inventory.models.Product)
    """
    return ProductImageImporter.create(product)
