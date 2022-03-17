"""Models for products."""

import random
import string
from collections import defaultdict

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from polymorphic.models import PolymorphicManager, PolymorphicModel

from .suppliers import Supplier

UNIQUE_SKU_ATTEMPTS = 100


class VariationOption(models.Model):
    """Model for variation options."""

    class Meta:
        """Meta class for VariationOption."""

        verbose_name = "Variation Option"
        verbose_name_plural = "Variation Options"
        ordering = ("ordering",)

    name = models.CharField(max_length=50, unique=True)
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ListingAttribute(models.Model):
    """Model for listing attributes."""

    class Meta:
        """Meta class for ListingAttribute."""

        verbose_name = "Listing Attribute"
        verbose_name_plural = "Listing Attributes"
        ordering = ("ordering",)

    name = models.CharField(max_length=50, unique=True)
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PackageType(models.Model):
    """Model for package types."""

    name = models.CharField(max_length=50, unique=True)
    large_letter_compatible = models.BooleanField(default=False)
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)
    active = models.BooleanField(default=True)

    class Meta:
        """Meta class for PackageType."""

        verbose_name = "Package Type"
        verbose_name_plural = "Package Types"
        ordering = ("ordering",)

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Model for Brands."""

    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        """Meta class for Brand."""

        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    """Model for manufacturers."""

    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        """Meta class for Manufacturer."""

        verbose_name = "Manufacturer"
        verbose_name_plural = "Manufacturers"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Gender(models.Model):
    """Model for Amazon genders."""

    name = models.CharField(max_length=50)
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)
    active = models.BooleanField(default=True)

    class Meta:
        """Meta class for Gender."""

        verbose_name = "Gender"
        verbose_name_plural = "Genders"
        ordering = ("ordering",)

    def __str__(self):
        return self.name


class VATRate(models.Model):
    """Model for VAT rates."""

    name = models.CharField(max_length=50, unique=True)
    percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1)]
    )
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        """Meta class for VAT Rate."""

        verbose_name = "VAT Rate"
        verbose_name_plural = "VAT Rates"
        ordering = ["ordering"]

    def __str__(self):
        return self.name


class ProductRangeManager(models.Manager):
    """Manager for complete products."""

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of complete products."""
        return super().get_queryset(*args, **kwargs).filter(status=self.model.COMPLETE)


class CreatingProductRangeManager(models.Manager):
    """Manager for incomplete products."""

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of incomplete products."""
        return super().get_queryset(*args, **kwargs).filter(status=self.model.CREATING)


class ProductRange(models.Model):
    """Model for Product Ranges."""

    COMPLETE = "complete"
    CREATING = "creating"
    ERROR = "error"

    STATUS_CHOICES = (
        (COMPLETE, "Complete"),
        (CREATING, "Creating"),
        (ERROR, "Error"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CREATING)

    sku = models.CharField(
        max_length=255, unique=True, db_index=True, blank=False, null=False
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    amazon_search_terms = models.TextField(blank=True, default="")
    amazon_bullet_points = models.TextField(blank=True, default="")
    end_of_line = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    managed_by = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name="product_ranges"
    )

    objects = models.Manager()
    ranges = ProductRangeManager()
    creating = CreatingProductRangeManager()

    class Meta:
        """Meta class for Product Ranges."""

        verbose_name = "Product Range"
        verbose_name_plural = "Product Ranges"

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def get_absolute_url(self):
        """Return the absolute url for the product range."""
        return reverse("inventory:product_range", kwargs={"range_pk": self.pk})

    def complete_new_range(self):
        """Make product range complete and active."""
        self.status = self.COMPLETE
        self.save()

    def has_variations(self):
        """Return True if the product has multiple variations, otherwise return False."""
        return self.products.count() > 1

    def variation_options(self):
        """Return the Range's variable product options."""
        return (
            VariationOptionValue.objects.filter(product__product_range=self)
            .values_list("variation_option__name", flat=True)
            .distinct()
            .order_by()
        )

    def listing_attributes(self):
        """Return the Range's listing product options."""
        return (
            ListingAttributeValue.objects.filter(product__product_range=self)
            .values_list("listing_attribute__name", flat=True)
            .distinct()
            .order_by()
        )

    def variation_option_values(self):
        """Return a dict of varition keys and values."""
        variation_values = VariationOptionValue.objects.filter(
            product__product_range=self
        ).order_by("variation_option", "value")
        variation_options = defaultdict(list)
        for value in variation_values:
            if value.value not in variation_options[value.variation_option]:
                variation_options[value.variation_option].append(value.value)
        return dict(variation_options)

    def variation_values(self):
        """Return a list of the product range's variation option values."""
        return (
            VariationOptionValue.objects.filter(product__product_range=self)
            .distinct()
            .order_by()
            .values_list("value", flat=True)
        )

    def listing_attribute_values(self):
        """Return a list of the product range's listing attribute values."""
        return (
            ListingAttribute.objects.filter(product__product_range=self)
            .values_list("value", flat=True)
            .distinct()
            .order_by()
        )


class ProductManager(PolymorphicManager):
    """Manager for complete products."""

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of complete products."""
        return (
            super()
            .get_queryset(*args, **kwargs)
            .filter(product_range__status=ProductRange.COMPLETE)
        )


class CreatingProductManager(PolymorphicManager):
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

    objects = PolymorphicManager()
    products = ProductManager()
    creating = CreatingProductManager()

    class Meta:
        """Meta class for the BaseProduct model."""

        verbose_name = "Base Product"
        verbose_name_plural = "Base Products"

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

    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="products"
    )
    supplier_sku = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=20)
    supplier_barcode = models.CharField(max_length=20, blank=True, null=True)
    purchase_price = models.DecimalField(decimal_places=2, max_digits=8)
    vat_rate = models.ForeignKey(
        VATRate, on_delete=models.PROTECT, related_name="products"
    )
    retail_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True
    )
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.PROTECT, related_name="products"
    )
    package_type = models.ForeignKey(
        PackageType, on_delete=models.PROTECT, related_name="products"
    )
    weight_grams = models.PositiveSmallIntegerField()
    length_mm = models.PositiveSmallIntegerField(blank=True, null=True)
    height_mm = models.PositiveSmallIntegerField(blank=True, null=True)
    width_mm = models.PositiveSmallIntegerField(blank=True, null=True)
    end_of_line = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    hs_code = models.CharField(max_length=50)
    gender = models.ForeignKey(
        Gender,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    range_order = models.PositiveSmallIntegerField(default=0)

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


class SingleProduct(Product):
    """Model for single products."""

    pass


class VariationProduct(Product):
    """Model for variation products."""

    pass


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


class CombinationProduct(BaseProduct):
    """Model for combination items."""

    products = models.ManyToManyField(
        Product,
        through=CombinationProductLink,
        related_name="combination_products",
    )


class VariationOptionValue(models.Model):
    """Model for product variation option values."""

    product = models.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="variation_option_values",
    )
    variation_option = models.ForeignKey(
        VariationOption,
        on_delete=models.PROTECT,
        related_name="variation_option_values",
    )
    value = models.CharField(max_length=255)

    class Meta:
        """Meta class for VariationOptionValue."""

        verbose_name = "Variation Option Value"
        verbose_name_plural = "Variation Option Values"
        ordering = ("variation_option", "value")
        unique_together = ("product", "variation_option")

    def __str__(self):
        return (
            f"VariationOptionValue: {self.product.sku} - "
            f"{self.variation_option.name}"
        )


class ListingAttributeValue(models.Model):
    """Model for product listing attribute values."""

    product = models.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="listing_attribute_values",
    )
    listing_attribute = models.ForeignKey(
        ListingAttribute,
        on_delete=models.PROTECT,
        related_name="listing_attribute_values",
    )
    value = models.CharField(max_length=255)

    class Meta:
        """Meta class for ListingAttributeValue."""

        verbose_name = "Listing Attribute Value"
        verbose_name_plural = "Listing Attribute Values"
        ordering = ("value",)
        unique_together = ("product", "listing_attribute")

    def __str__(self):
        return (
            f"ListingAttributeValue: {self.product.sku} - "
            f"{self.listing_attribute.name}"
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
    existing_skus = set(Product.products.values_list("sku", flat=True).distinct())
    return unique_sku(existing_skus=existing_skus, sku_function=generate_sku)


def new_range_sku():
    """Return a new product range SKU."""
    existing_skus = set(ProductRange.ranges.values_list("sku", flat=True).distinct())
    return unique_sku(existing_skus=existing_skus, sku_function=generate_range_sku)
