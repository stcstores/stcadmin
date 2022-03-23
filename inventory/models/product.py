"""Models for products."""

import random
import string
from itertools import chain

from django.apps import apps
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from polymorphic.models import PolymorphicManager, PolymorphicModel

from .product_attribute import (
    Brand,
    Gender,
    Manufacturer,
    PackageType,
    VariationOptionValue,
    VATRate,
)
from .product_range import ProductRange
from .supplier import Supplier

UNIQUE_SKU_ATTEMPTS = 100


class BaseProductManager(PolymorphicManager):
    """Base product manager for products."""

    def variations(self, *args, **kwargs):
        """Return a queryset of complete products."""
        return (
            super(PolymorphicManager, self)
            .all(*args, **kwargs)
            .filter(product_range__status=ProductRange.COMPLETE)
            .not_instance_of(InitialVariation)
        )

    def active(self, *args, **kwargs):
        """Return a queryset of active products."""
        return self.variations().filter(is_end_of_line=False)


class CreatingProductManager(BaseProductManager):
    """Manager for incomplete products."""

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of incomplete products."""
        return (
            super()
            .get_queryset(*args, **kwargs)
            .filter(product_range__status=ProductRange.CREATING)
        )


class BaseProduct(PolymorphicModel):
    """Base model for products."""

    product_range = models.ForeignKey(
        ProductRange, on_delete=models.PROTECT, related_name="products"
    )
    sku = models.CharField(
        max_length=255, unique=True, db_index=True, blank=False, null=False
    )
    retail_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="products"
    )
    supplier_sku = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=20)
    supplier_barcode = models.CharField(max_length=20, blank=True, null=True)
    package_type = models.ForeignKey(
        PackageType, on_delete=models.PROTECT, related_name="products"
    )
    length_mm = models.PositiveSmallIntegerField(blank=True, null=True)
    height_mm = models.PositiveSmallIntegerField(blank=True, null=True)
    width_mm = models.PositiveSmallIntegerField(blank=True, null=True)
    is_end_of_line = models.BooleanField(default=False)
    created_at = models.DateField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    range_order = models.PositiveSmallIntegerField(default=0)
    latest_stock_change = models.ForeignKey(
        "StockLevelHistory",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        editable=False,
    )

    objects = BaseProductManager()
    creating = CreatingProductManager()

    class Meta:
        """Meta class for the BaseProduct model."""

        verbose_name = "Base Product"
        verbose_name_plural = "Base Products"
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["supplier_sku"]),
            models.Index(fields=["barcode"]),
            models.Index(fields=["supplier_barcode"]),
        ]
        ordering = (
            "product_range",
            "range_order",
        )
        base_manager_name = "objects"

    def __str__(self):
        return f"{self.sku}: {self.full_name}"

    def get_absolute_url(self):
        """Return the absolute url of the object."""
        return reverse("inventory:product", kwargs={"pk": self.pk})

    @property
    def full_name(self):
        """Return the product name with any extensions."""
        return " - ".join([self.product_range.name] + self.name_extensions())

    @property
    def range_sku(self):
        """Return the product's Range SKU."""
        return self.product_range.sku

    def name_extensions(self):
        """Return additions to the product name."""
        extensions = list(self.variation_values())
        return extensions

    def name(self):
        """Return the product's name."""
        return self.product_range.name

    def variation(self):
        """Return the product's variation product options as a dict."""
        options = VariationOptionValue.objects.filter(product=self)
        return {option.variation_option.name: option.value for option in options}

    # def listing_options(self):
    #     """Return the product's listing product options as a dict."""
    #     return {
    #         option.product_option: option for option in self.selected_listing_options()
    #     }

    def variable_options(self):
        """Return list of Product Options which are variable for the range."""
        return (
            VariationOptionValue.objects.filter(product=self)
            .values_list("name", "value")
            .order_by("variation_option", "value")
        )

    def variation_values(self):
        """Return a list of the product's variation option values."""
        return (
            VariationOptionValue.objects.filter(product=self)
            .values_list("value", flat=True)
            .order_by("variation_option", "value")
        )

    # def selected_listing_options(self):
    #     """Return list of Product Options which are listing options for the range."""
    #     options = self.product_range.listing_options()
    #     return self.product_options.filter(product_option__in=options).order_by(
    #         "product_option"
    #     )


class Product(BaseProduct):
    """Model for inventory products."""

    purchase_price = models.DecimalField(decimal_places=2, max_digits=8)
    vat_rate = models.ForeignKey(
        VATRate, on_delete=models.PROTECT, related_name="products"
    )
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.PROTECT, related_name="products"
    )
    weight_grams = models.PositiveSmallIntegerField()

    hs_code = models.CharField(max_length=50)
    gender = models.ForeignKey(
        Gender,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )

    class Meta:
        """Meta class for Products."""

        verbose_name = "Product"
        verbose_name_plural = "Products"

    def stock_level(self):
        """Return the products current stock level in Cloud Commerce."""
        raise NotImplementedError()

    def name_extensions(self):
        """Return additions to the product name."""
        extensions = super().name_extensions()
        if self.supplier_sku:
            extensions.append(self.supplier_sku)
        return extensions

    def update_stock_level(self, *, old, new):
        """Set the product's stock level in Cloud Commerce."""
        raise NotImplementedError()


class InitialVariation(Product):
    """Model for initial product variation data."""

    ignore_fields = {"baseproduct_ptr", "product_ptr", "id", "sku"}

    def _to_dict(self):
        """Return a dict of attributes."""
        opts = self._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
            if f.name in self.ignore_fields:
                continue
            if not getattr(f, "editable", False):
                continue
            data[f.name] = getattr(self, f.name)
        return data

    def _create_variation(self, variation):
        product_kwargs = self._to_dict()
        product_kwargs["sku"] = new_product_sku()
        product = Product(**product_kwargs)
        product.save()
        for option, value in variation.items():
            variation_option = apps.get_model(
                "inventory", "VariationOption"
            ).objects.get(name=option)
            VariationOptionValue(
                product=product, variation_option=variation_option, value=value
            ).save()
        return product

    @transaction.atomic
    def create_variations(self, variations):
        """Create variation products."""
        created_variations = []
        for variation in variations:
            new_variation = self._create_variation(variation)
            created_variations.append(new_variation)
        return created_variations


class MultipackProduct(BaseProduct):
    """Model for multipack items."""

    base_product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="multipacks"
    )
    quantity = models.PositiveIntegerField()
    name = models.CharField(max_length=50)


class CombinationProductLink(models.Model):
    """Model for linking combination products."""

    class Meta:
        """Meta class for the CombinationProductLink model."""

        verbose_name = "Combination Product Link"
        verbose_name_plural = "Combination Product Links"
        unique_together = ("product", "combination_product")

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="combination_product_links",
    )
    combination_product = models.ForeignKey(
        "CombinationProduct",
        on_delete=models.CASCADE,
        related_name="combination_product_links",
    )
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.combination_product.sku} contains {self.quantity} {self.product.sku}"


class CombinationProduct(BaseProduct):
    """Model for combination items."""

    class Meta:
        """Meta class for the CombinationProductLink model."""

        verbose_name = "Combination Product"
        verbose_name_plural = "Combination Products"

    products = models.ManyToManyField(
        Product,
        through=CombinationProductLink,
        related_name="combination_products",
    )


def generate_sku():
    """Return a Product SKU."""

    def get_character_block():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return "_".join((get_character_block() for _ in range(3)))


def generate_range_sku():
    """Return a Product Range SKU."""
    return f"RNG_{generate_sku()}"


def unique_sku(existing_skus, sku_function):
    """Generate a unique SKU."""
    remaining_attempts = UNIQUE_SKU_ATTEMPTS
    while True:
        sku = sku_function()
        if sku not in existing_skus:
            return sku
        remaining_attempts -= 1
        if remaining_attempts == 0:
            raise Exception(
                f"Did not generate a unique SKU in {UNIQUE_SKU_ATTEMPTS} attemtps."
            )


def new_product_sku():
    """Return a new product SKU."""
    existing_skus = set(Product.objects.values_list("sku", flat=True).distinct())
    return unique_sku(existing_skus=existing_skus, sku_function=generate_sku)


def new_range_sku():
    """Return a new product range SKU."""
    existing_skus = set(ProductRange.ranges.values_list("sku", flat=True).distinct())
    return unique_sku(existing_skus=existing_skus, sku_function=generate_range_sku)
