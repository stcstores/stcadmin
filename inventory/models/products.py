"""Models for products."""

import random
import string

from ccapi import CCAPI
from django.db import models

from . import product_options
from .locations import Bay
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
    department = models.ForeignKey(product_options.Department, on_delete=models.PROTECT)
    variation_options = models.ManyToManyField(
        product_options.ProductOption, blank=True
    )
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

    def set_product_option_variable(self, option):
        """Set a Product Option as variable.

        Args:
            option: inventory.product_options.ProductOption or str(ProductOption.name).
        """
        if isinstance(option, str):
            option = product_options.ProductOption.objects.get(name=option)
        self.variation_options.add(option)

    def set_variable_options(self, options):
        """Replace the variable product options.

        Args:
            options: list(ProductOption or str(ProductOption.name))
        """
        set_options = []
        for option in options:
            if isinstance(option, str):
                option = product_options.ProductOption.objects.get(name=option)
            set_options.append(option)
        self.variation_options.set(set_options)

    def product_count(self):
        """Return the number of products in this Range."""
        return self.product_set.count()


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
    name = models.CharField(max_length=255)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    supplier_SKU = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=20)
    purchase_price = models.DecimalField(decimal_places=2, max_digits=8)
    VAT_rate = models.ForeignKey(VATRate, on_delete=models.PROTECT)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    retail_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True
    )
    brand = models.ForeignKey(product_options.Brand, on_delete=models.PROTECT)
    manufacturer = models.ForeignKey(
        product_options.Manufacturer, on_delete=models.PROTECT
    )
    description = models.TextField()
    package_type = models.ForeignKey(
        product_options.PackageType, on_delete=models.PROTECT
    )
    international_shipping = models.ForeignKey(
        product_options.InternationalShipping, on_delete=models.PROTECT
    )
    bays = models.ManyToManyField(Bay, blank=True)
    weight_grams = models.PositiveSmallIntegerField()
    length_mm = models.PositiveSmallIntegerField()
    height_mm = models.PositiveSmallIntegerField()
    width_mm = models.PositiveSmallIntegerField()
    amazon_search_terms = models.TextField()
    amazon_bullet_points = models.TextField()
    product_options = models.ManyToManyField(
        product_options.ProductOptionValue, blank=True
    )
    multipack = models.BooleanField(default=False)
    end_of_line = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CREATING)
    date_created = models.DateField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for Products."""

        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.SKU}: {self.full_name}"

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

    @property
    def full_name(self):
        """Return the product name with any extensions."""
        return " - ".join([self.name] + self.name_extensions())

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
        variable_options = self.product_range.variation_options.all()
        return self.product_options.filter(product_option__in=variable_options)

    def update_stock_level(self, stock_level):
        """Set the product's stock level in Cloud Commerce."""
        CCAPI.update_product_stock_level(
            product_id=self.product_ID,
            new_stock_level=stock_level,
            old_stock_level=self.stock_level,
        )

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

    def CC_create_product(self):
        """Create the product in Cloud Commerce."""
        CCAPI.create_product(
            self.range_ID,
            self.name,
            self.barcode,
            sku=self.SKU,
            description=self.description,
            vat_rate_id=int(self.VAT_rate.percentage * 100),
        )
