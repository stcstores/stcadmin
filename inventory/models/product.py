"""Models for products."""

import random
import string
from itertools import chain

from django.apps import apps
from django.contrib.postgres.search import SearchVector
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet
from polymorphic.models import PolymorphicModel

from .product_attribute import (
    Brand,
    Manufacturer,
    PackageType,
    VariationOptionValue,
    VATRate,
)
from .product_range import ProductRange
from .supplier import Supplier

UNIQUE_SKU_ATTEMPTS = 100


class ProductQueryset(PolymorphicQuerySet):
    """Custom queryset for products."""

    def complete(self):
        """Return complete products."""
        return self.filter(product_range__status=ProductRange.COMPLETE).select_related(
            "product_range"
        )

    def incomplete(self):
        """Return incomplete products."""
        return self.filter(product_range__status=ProductRange.CREATING).select_related(
            "product_range"
        )

    def simple(self):
        """Return basic products (not initial variations, multipacks or combinations)."""
        return (
            self.filter()
            .not_instance_of(InitialVariation)
            .not_instance_of(MultipackProduct)
            .not_instance_of(CombinationProduct)
        )

    def variations(self):
        """Return a queryset of complete products."""
        return self.filter().not_instance_of(InitialVariation)

    def active(self):
        """Return a queryset of active products."""
        return self.filter(is_end_of_line=False).select_related("latest_stock_change")


class ProductManager(PolymorphicManager):
    """Manager for Product models."""

    queryset_class = ProductQueryset

    SEARCH_FIELDS = (
        "product_range__name",
        "product_range__sku",
        "sku",
        "supplier_sku",
        "barcode",
    )

    def text_search(self, search_term, end_of_line=None):
        """
        Text search for product models.

        Matches on product.sku, product.supplier_sku, product.barcode,
        product.product_range.name and product.product_range.sku.

        Args:
            search_term (str): The text to search for.

        Kwargs:
            end_of_line (bool|None) default None: If True only end of line products
                will be returned, if False no end of line products will be returned,
                otherwise no filtering will be done based on end of line status.
        """
        qs = (
            self.annotate(search=SearchVector(*self.SEARCH_FIELDS))
            .filter(search=search_term)
            .select_related("product_range")
        )
        if end_of_line is True:
            qs = qs.filter(is_end_of_line=True, product_range__is_end_of_line=True)
        elif end_of_line is False:
            qs = qs.exclude(is_end_of_line=True, product_range__is_end_of_line=True)
        return qs


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
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    range_order = models.PositiveSmallIntegerField(default=0)
    latest_stock_change = models.ForeignKey(
        "StockLevelHistory",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        editable=False,
    )

    objects = ProductManager.from_queryset(ProductQueryset)()

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
        options = self.variation_option_values.all()
        return {option.variation_option.name: option.value for option in options}

    def listing_attributes(self):
        """Return the product's listing product options as a dict."""
        options = self.listing_attribute_values.all()
        return {option.listing_attribute.name: option.value for option in options}

    def attributes(self):
        """Return a combined dict of variation options and listing attributes."""
        variation_options = self.variation()
        listing_attributes = self.listing_attributes()
        return listing_attributes | variation_options

    def variable_options(self):
        """Return list of Product Options which are variable for the range."""
        return self.variation_option_values.values_list(
            "variation_option__name", flat=True
        )

    def variation_values(self):
        """Return a list of the product's variation option values."""
        return (
            self.variation_option_values.all()
            .values_list("value", flat=True)
            .order_by("variation_option", "value")
        )


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

    @property
    def weight_grams(self):
        """Return the weight of the multipack product."""
        return self.base_product.weight_grams * self.quantity

    @property
    def purchase_price(self):
        """Return the purchase price of the multipack product."""
        return self.base_product.purchase_price * self.quantity

    @property
    def brand(self):
        """Return the mutlipack proudct's brand."""
        return self.base_product.brand

    @property
    def manufacturer(self):
        """Return the mutlipack proudct's manufacturer."""
        return self.base_product.manufacturer

    @property
    def vat_rate(self):
        """Return the mutlipack proudct's VAT rate."""
        return self.base_product.vat_rate

    @property
    def hs_code(self):
        """Return the mutlipack proudct's HS code."""
        return self.base_product.hs_code


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
