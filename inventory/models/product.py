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

from inventory.models.location import ProductBayLink

from .product_attribute import (
    Brand,
    Manufacturer,
    PackageType,
    PackingRequirement,
    VariationOptionValue,
    VATRate,
)
from .product_image import ProductImage, ProductImageLink, ProductRangeImageLink
from .product_range import ProductRange
from .supplier import Supplier

UNIQUE_SKU_ATTEMPTS = 100


class EndOfLineReason(models.Model):
    """Model for reasons a product has been marked end of line."""

    name = models.CharField(max_length=255, unique=True, db_index=True)
    short_name = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        """Meta class for EndOfLineReason."""

        verbose_name = "End of Line Reason"
        verbose_name_plural = "End of Line Reasons"

    def __str__(self):
        return self.name

    def short(self):
        """Return short_name if it is not None, else name."""
        if self.short_name:
            return self.short_name
        return self.name


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
        return self.filter(is_archived=False)


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

    def text_search(self, search_term, archived=None):
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
        if archived is True:
            qs = qs.filter(is_archived=True)
        elif archived is False:
            qs = qs.exclude(is_archived=True)
        return qs


class BaseProduct(PolymorphicModel):
    """Base model for products."""

    product_range = models.ForeignKey(
        ProductRange,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Product Range",
    )
    sku = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        blank=False,
        null=False,
        verbose_name="SKU",
    )
    retail_price = models.DecimalField(
        decimal_places=2,
        max_digits=8,
        null=True,
        blank=True,
        verbose_name="Retail Price",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Supplier",
    )
    additional_suppliers = models.ManyToManyField(
        Supplier,
        related_name="additional_products",
        verbose_name="Additional Suppliers",
        blank=True,
    )
    supplier_sku = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Supplier SKU"
    )
    barcode = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Barcode"
    )
    supplier_barcode = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Supplier Barcode"
    )
    package_type = models.ForeignKey(
        PackageType,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Package Type",
    )

    width = models.PositiveSmallIntegerField(default=0, verbose_name="Width (cm)")
    height = models.PositiveSmallIntegerField(default=0, verbose_name="Height (cm)")
    depth = models.PositiveSmallIntegerField(default=0, verbose_name="Depth (cm)")

    notes = models.TextField(blank=True, default="")

    is_end_of_line = models.BooleanField(default=False, verbose_name="Is EOL")
    is_archived = models.BooleanField(default=False, verbose_name="Is Archived")
    end_of_line_reason = models.ForeignKey(
        EndOfLineReason,
        on_delete=models.PROTECT,
        related_name="products",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    range_order = models.PositiveSmallIntegerField(default=0)

    images = models.ManyToManyField(
        ProductImage, through=ProductImageLink, related_name="image_products"
    )

    packing_requirements = models.ManyToManyField(
        PackingRequirement, related_name="products"
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
        ordering = ("product_range", "is_archived", "is_end_of_line", "range_order")
        base_manager_name = "objects"

    def __str__(self):
        return f"{self.sku}: {self.full_name}"

    def get_absolute_url(self):
        """Return the absolute url of the object."""
        return reverse("inventory:edit_product", kwargs={"pk": self.pk})

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
        options = self.variation_option_values.all().order_by("variation_option")
        return {option.variation_option.name: option.value for option in options}

    def listing_attributes(self):
        """Return the product's listing product options as a dict."""
        options = self.listing_attribute_values.all().order_by("listing_attribute")
        return {option.listing_attribute.name: option.value for option in options}

    def attributes(self):
        """Return a combined dict of variation options and listing attributes."""
        variation_options = self.variation()
        listing_attributes = self.listing_attributes()
        return listing_attributes | variation_options

    def variable_options(self):
        """Return list of Product Options which are variable for the range."""
        return list(
            self.variation_option_values.values_list(
                "variation_option__name", flat=True
            )
        )

    def variation_values(self):
        """Return a list of the product's variation option values."""
        return list(
            self.variation_option_values.all()
            .values_list("value", flat=True)
            .order_by("variation_option", "value")
        )

    def get_primary_image(self):
        """Return the primary image for the product or None if no image is available."""
        image_link = ProductImageLink.objects.filter(product=self).first()
        if image_link is None:
            image_link = ProductRangeImageLink.objects.filter(
                product_range=self.product_range
            ).first()
        if image_link is not None:
            return image_link.image
        return None

    def bays(self):
        """Return a list of bays containing the product."""
        return [link.bay for link in self.product_bay_links.all()]

    @transaction.atomic
    def set_end_of_line(self, reason):
        """Set the product and any combination or multipack products containing it as EOL."""
        MultipackProduct.objects.filter(base_product=self).update(
            is_end_of_line=True, end_of_line_reason=reason
        )
        CombinationProduct.objects.filter(products=self).update(
            is_end_of_line=True, end_of_line_reason=reason
        )
        self.is_end_of_line = True
        self.end_of_line_reason = reason
        self.save()

    @transaction.atomic
    def set_archived(self):
        """
        Set the product as archived.

        Any combination or multipack products containing this product will also be
        marked archived.
        """
        MultipackProduct.objects.filter(base_product=self).update(
            is_archived=True, is_end_of_line=True
        )
        CombinationProduct.objects.filter(products=self).update(
            is_archived=True, is_end_of_line=True
        )
        self.is_archived = True
        self.is_end_of_line = True
        self.save()


class Product(BaseProduct):
    """Model for inventory products."""

    purchase_price = models.DecimalField(
        decimal_places=2, max_digits=8, verbose_name="Purchase Price"
    )
    vat_rate = models.ForeignKey(
        VATRate,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="VAT Rate",
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, related_name="products", verbose_name="Brand"
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Manufacturer",
    )
    weight_grams = models.PositiveSmallIntegerField(verbose_name="Weight (g)")

    hs_code = models.CharField(max_length=50, verbose_name="HS Code")

    is_flammable = models.BooleanField(default=False, verbose_name="Is Flammable")

    class Meta:
        """Meta class for Products."""

        verbose_name = "Product"
        verbose_name_plural = "Products"

    def name_extensions(self):
        """Return additions to the product name."""
        extensions = super().name_extensions()
        if self.supplier_sku:
            extensions.append(self.supplier_sku)
        return extensions


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
        del product_kwargs["images"]
        del product_kwargs["additional_suppliers"]
        del product_kwargs["packing_requirements"]
        product = Product(**product_kwargs)
        product.save()
        product.packing_requirements.set(self.packing_requirements.all())
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

    @property
    def product_bay_links(self):
        """Return a queryset of linked product bays."""
        return self.base_product.product_bay_links

    @property
    def is_flammable(self):
        """Return True if the multipack is flammable, else False."""
        return self.base_product.is_flammable


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

    def _product_ids(self):
        return self.products.values_list("pk", flat=True)

    @property
    def product_bay_links(self):
        """Return a queryset of all linked product bays."""
        return ProductBayLink.objects.filter(product__pk__in=self._product_ids())

    @property
    def vat_rate(self):
        """Return the highest combined product VAT rate."""
        return (
            self.products.select_related("vat_rate")
            .order_by("-vat_rate__percentage")
            .first()
            .vat_rate
        )

    @property
    def brand(self):
        """Return the product's brand."""
        return self.products.first().brand

    @property
    def manufacturer(self):
        """Return the product's manufacturer."""
        return self.products.first().manufacturer

    @property
    def hs_code(self):
        """Return the product's HS code."""
        return self.products.first().hs_code

    @property
    def weight_grams(self):
        """Return the combined product weight."""
        return sum((self.products.all().values_list("weight_grams", flat=True)))

    @property
    def purchase_price(self):
        """Return the combined product purchase_price."""
        return sum((self.products.all().values_list("purchase_price", flat=True)))

    @property
    def is_flammable(self):
        """Return True if the combination product is flammable, else False."""
        return self.products.filter(is_flammable=True).exists()


def generate_sku():
    """Return a Product SKU."""

    def get_character_block():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return "-".join((get_character_block() for _ in range(3)))


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
