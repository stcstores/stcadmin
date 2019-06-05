"""Models for products."""

import random
import string

from ccapi import CCAPI
from django.db import models

from .locations import Bay
from .product_options import (
    Brand,
    Department,
    Gender,
    InternationalShipping,
    Manufacturer,
    PackageType,
    ProductOption,
    ProductOptionValue,
)
from .suppliers import Supplier
from .vat_rates import VATRate

UNIQUE_SKU_ATTEMPTS = 100


def generate_SKU():
    """Return a Product SKU."""
    pass

    def get_character_block():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return "_".join((get_character_block() for _ in range(3)))


def unique_SKU(existing_SKUs, SKU_function):
    """Generate a unique SKU."""
    remaining_attempts = UNIQUE_SKU_ATTEMPTS
    while True:
        SKU = SKU_function()
        if SKU not in existing_SKUs:
            return SKU
        if remaining_attempts == 0:
            raise Exception(
                f"Did not generate a unique SKU in {UNIQUE_SKU_ATTEMPTS} attemtps."
            )


class ProductRange(models.Model):
    """Model for Product Ranges."""

    range_ID = models.CharField(max_length=50, db_index=True, unique=True)
    SKU = models.CharField(max_length=15, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    description = models.TextField(blank=True, default="")
    product_options = models.ManyToManyField(
        ProductOption, blank=True, through="ProductRangeSelectedOption"
    )
    amazon_search_terms = models.TextField(blank=True, default="")
    amazon_bullet_points = models.TextField(blank=True, default="")
    end_of_line = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    class Meta:
        """Meta class for Product Ranges."""

        verbose_name = "Product Range"
        verbose_name_plural = "Product Ranges"

    def __str__(self):
        return f"{self.SKU} - {self.name}"

    @classmethod
    def get_new_SKU(cls):
        """Return an unused Range SKU."""
        existing_SKUs = cls._base_manager.values_list("SKU", flat=True)
        return unique_SKU(existing_SKUs, cls.generate_SKU)

    @staticmethod
    def generate_SKU():
        """Return a Product Range SKU."""
        return f"RNG_{generate_SKU()}"

    def clean(self, *args, **kwargs):
        """Save the model instance."""
        if not self.SKU:
            self.SKU = self.get_new_SKU()
        if not self.range_ID:
            self.range_ID = self.create_CC_range()
        super().clean(*args, **kwargs)

    def create_CC_range(self):
        """Create a new Product Range in Cloud Commerce."""
        return CCAPI.create_range(self.name, sku=self.SKU)

    def product_count(self):
        """Return the number of products in this Range."""
        return self.product_set.count()

    def variation_options(self):
        """Return the Range's variable product options."""
        product_options = ProductRangeSelectedOption.objects.filter(
            product_range=self, variation=True
        ).values_list("product_option", flat=True)
        return ProductOption.objects.filter(id__in=product_options)

    def listing_options(self):
        """Return the Range's listing product options."""
        product_option_IDs = ProductRangeSelectedOption.objects.filter(
            product_range=self, variation=False
        ).values_list("product_option", flat=True)
        return ProductOption.objects.filter(id__in=product_option_IDs)

    def products(self):
        """Return a queryset of the Product Range's products."""
        return self.product_set.all().order_by("range_order", "id")

    def has_variations(self):
        """Return True if the product has multiple variations, otherwise return False."""
        return self.product_set.count() > 1

    def variation_values(self):
        """Return a dict of {option_name: set(option_values)} for the ranges variable options."""
        values = ProductOptionValueLink.objects.filter(
            product_option_value__product_option__in=self.variation_options(),
            product__product_range=self,
        )
        option_values = {}
        for value in values:
            option_name = value.product_option_value.product_option.name
            option_value = value.product_option_value.value
            if option_name not in option_values:
                option_values[option_name] = []
            option_values[option_name].append(option_value)
        for option, value_list in option_values.items():
            option_values[option] = set(value_list)
        return option_values


class Product(models.Model):
    """Model for inventory products."""

    COMPLETE = "complete"
    CREATING = "creating"
    UPDATING = "updating"
    ERROR = "error"

    STATUS_CHOICES = (
        (COMPLETE, "Complete"),
        (CREATING, "Creating"),
        (UPDATING, "Updating"),
        (ERROR, "Error"),
    )

    product_ID = models.CharField(max_length=50, unique=True, db_index=True)
    product_range = models.ForeignKey(ProductRange, on_delete=models.PROTECT)
    SKU = models.CharField(max_length=255, unique=True, db_index=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    supplier_SKU = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=20)
    purchase_price = models.DecimalField(decimal_places=2, max_digits=8)
    VAT_rate = models.ForeignKey(VATRate, on_delete=models.PROTECT)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    retail_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True
    )
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    package_type = models.ForeignKey(PackageType, on_delete=models.PROTECT)
    international_shipping = models.ForeignKey(
        InternationalShipping, on_delete=models.PROTECT
    )
    bays = models.ManyToManyField(Bay, blank=True)
    weight_grams = models.PositiveSmallIntegerField()
    length_mm = models.PositiveSmallIntegerField()
    height_mm = models.PositiveSmallIntegerField()
    width_mm = models.PositiveSmallIntegerField()
    product_options = models.ManyToManyField(
        ProductOptionValue, blank=True, through="ProductOptionValueLink"
    )
    multipack = models.BooleanField(default=False)
    end_of_line = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CREATING)
    date_created = models.DateField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    gender = models.ForeignKey(Gender, null=True, on_delete=models.SET_NULL)
    range_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        """Meta class for Products."""

        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.SKU}: {self.full_name}"

    def name(self):
        """Return the product's name."""
        return self.product_range.name

    def save(self, *args, **kwargs):
        """Create a new product if the product ID is not set."""
        if not self.product_ID:
            self.product_ID = self.CC_create_product()
        super().save(*args, **kwargs)

    def variation(self):
        """Return the product's variation product options as a dict."""
        return {
            option.product_option.name: option.value
            for option in self.variable_options()
        }

    def listing_options(self):
        """Return the product's listing product options as a dict."""
        return {
            option.product_option.name: option.value
            for option in self.selected_listing_options()
        }

    @property
    def full_name(self):
        """Return the product name with any extensions."""
        return " - ".join([self.product_range.name] + self.name_extensions())

    @staticmethod
    def generate_SKU():
        """Return a Product SKU."""
        return generate_SKU()

    @property
    def range_SKU(self):
        """Return the product's Range SKU."""
        return self.product_range.SKU

    def variable_options(self):
        """Return list of Product Options which are variable for the range."""
        variable_options = self.product_range.variation_options()
        return self.product_options.filter(
            product_option__in=variable_options
        ).order_by("product_option")

    def selected_listing_options(self):
        """Return list of Product Options which are listing options for the range."""
        variable_options = self.product_range.listing_options()
        return self.product_options.filter(
            product_option__in=variable_options
        ).order_by("product_option")

    def update_stock_level(self, *, old, new):
        """Set the product's stock level in Cloud Commerce."""
        CCAPI.update_product_stock_level(
            product_id=self.product_ID, old_stock_level=old, new_stock_level=new
        )
        return self.stock_level()

    def department(self):
        """Return the Product's department."""
        return self.product_range.department

    def stock_level(self):
        """Return the products current stock level in Cloud Commerce."""
        product = CCAPI.get_product(self.product_ID)
        return product.stock_level

    def name_extensions(self):
        """Return additions to the product name."""
        extensions = [_.value for _ in self.variable_options().all()]
        if self.supplier_SKU:
            extensions.append(self.supplier_SKU)
        return extensions

    def product_option_value(self, option_name):
        """
        Return the value of a product option.

        Returns:
            The value of the product option with name option_name for the product if it
            exists, otherwise returns None.

        """
        try:
            return self.product_options.get(product_option__name=option_name).value
        except ProductOptionValue.DoesNotExist:
            return None

    def CC_create_product(self):
        """Create the product in Cloud Commerce."""
        CCAPI.create_product(
            self.product_range.range_ID,
            self.product_range.name,
            self.barcode,
            sku=self.SKU,
            description=self.description,
            vat_rate_id=int(self.VAT_rate.percentage * 100),
        )


class ProductRangeSelectedOption(models.Model):
    """Model for linking Product Ranges to Product Options."""

    product_range = models.ForeignKey(ProductRange, on_delete=models.CASCADE)
    product_option = models.ForeignKey(ProductOption, on_delete=models.CASCADE)
    variation = models.BooleanField()

    class Meta:
        """Meta class for ProductRangeVariableOption."""

        verbose_name = "ProductRangeSelectedOption"
        verbose_name_plural = "ProductRangeSelectedOptions"
        ordering = ("product_option",)
        unique_together = ("product_range", "product_option")

    def __str__(self):
        return (
            f"ProductRangeVariableOption: {self.product_range.SKU} - "
            f"{self.product_option.name}"
        )


class ProductOptionValueLink(models.Model):
    """Meta class for ProductRangeVariableOptions."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_option_value = models.ForeignKey(
        ProductOptionValue, on_delete=models.CASCADE
    )

    class Meta:
        """Meta class for ProductOptionValueLink."""

        verbose_name = "ProductOptionValueLink"
        verbose_name_plural = "ProductOptionValueLinks"
        ordering = ("product_option_value__product_option",)
        unique_together = ("product", "product_option_value")

    def __str__(self):
        return (
            f"ProductOptionValueLink: {self.product.SKU} - "
            f"{self.product_option_value.value}"
        )
