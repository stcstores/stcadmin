"""Models for products."""

import random
import string
from collections import defaultdict

from django.contrib.auth import get_user_model
from django.db import models

from .locations import Bay
from .suppliers import Supplier
from .vat_rates import VATRate

UNIQUE_SKU_ATTEMPTS = 100


class VariationOption(models.Model):
    """Model for variation options."""

    class Meta:
        """Meta class for VariationOption."""

        verbose_name = "Variation Option"
        verbose_name_plural = "Variation Option"
        ordering = ["ordering"]

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
        ordering = ["ordering"]

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
        ordering = ["ordering"]

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
        ordering = ["ordering"]

    def __str__(self):
        return self.name


class VariationOptionValue(models.Model):
    """Model for product variation option values."""

    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    variation_option = models.ForeignKey(VariationOption, on_delete=models.PROTECT)
    value = models.CharField(max_length=255)

    class Meta:
        """Meta class for VariationOptionValue."""

        verbose_name = "Variation Option Value"
        verbose_name_plural = "Variation Option Values"
        ordering = ("value",)

    def __str__(self):
        return (
            f"VariationOptionValue: {self.product.sku} - "
            f"{self.variation_option.name}"
        )


class ListingAttributeValue(models.Model):
    """Model for product listing attribute values."""

    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    listing_attribute = models.ForeignKey(ListingAttribute, on_delete=models.PROTECT)
    value = models.CharField(max_length=255)

    class Meta:
        """Meta class for ListingAttributeValue."""

        verbose_name = "Listing Attribute Value"
        verbose_name_plural = "Listing Attribute Values"
        ordering = ("value",)

    def __str__(self):
        return (
            f"VariationOptionValue: {self.product.sku} - "
            f"{self.variation_option.name}"
        )


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

    sku = models.CharField(max_length=15, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    amazon_search_terms = models.TextField(blank=True, default="")
    amazon_bullet_points = models.TextField(blank=True, default="")
    end_of_line = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    managed_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)

    class Meta:
        """Meta class for Product Ranges."""

        verbose_name = "Product Range"
        verbose_name_plural = "Product Ranges"

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def has_variations(self):
        """Return True if the product has multiple variations, otherwise return False."""
        return self.products().count() > 1

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

    def product_count(self):
        """Return the number of products in this Range."""
        return self.product_set.count()

    def products(self):
        """Return a queryset of the Product Range's products."""
        return self.product_set.all().order_by("range_order", "id")

    def variation_option_values(self):
        """Return a dict of varition keys and values."""
        variation_values = VariationOptionValue.objects.filter(
            product__product_range=self
        )
        variation_options = defaultdict(list)
        for value in variation_values:
            if value.value not in variation_options[value.variation_option]:
                variation_options[value.variation_option].append(value.value)
        return variation_options

    def variation_values(self):
        """Return a list of the product range's variation option values."""
        return (
            VariationOptionValue.objects.filter(product__product_range=self)
            .values_list("value", flat=True)
            .distinct()
            .order_by()
        )

    def listing_attribute_values(self):
        """Return a list of the product range's listing attribute values."""
        return (
            ListingAttribute.objects.filter(product__product_range=self)
            .values_list("value", flat=True)
            .distinct()
            .order_by()
        )


class Product(models.Model):
    """Model for inventory products."""

    product_range = models.ForeignKey(ProductRange, on_delete=models.PROTECT)
    sku = models.CharField(max_length=255, unique=True, db_index=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    supplier_sku = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=20)
    purchase_price = models.DecimalField(decimal_places=2, max_digits=8)
    vat_rate = models.ForeignKey(VATRate, on_delete=models.PROTECT)
    retail_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True
    )
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    package_type = models.ForeignKey(PackageType, on_delete=models.PROTECT)
    bays = models.ManyToManyField(Bay, blank=True)
    weight_grams = models.PositiveSmallIntegerField()
    length_mm = models.PositiveSmallIntegerField(blank=True, null=True)
    height_mm = models.PositiveSmallIntegerField(blank=True, null=True)
    width_mm = models.PositiveSmallIntegerField(blank=True, null=True)
    end_of_line = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    hs_code = models.CharField(max_length=50)
    gender = models.ForeignKey(Gender, null=True, blank=True, on_delete=models.SET_NULL)
    range_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        """Meta class for Products."""

        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.sku}: {self.full_name}"

    @property
    def full_name(self):
        """Return the product name with any extensions."""
        return " - ".join([self.product_range.name] + self.name_extensions())

    @property
    def range_sku(self):
        """Return the product's Range SKU."""
        return self.product_range.sku

    def name(self):
        """Return the product's name."""
        return self.product_range.name

    def variation(self):
        """Return the product's variation product options as a dict."""
        options = VariationOptionValue.objects.filter(product=self)
        return {option.variation_option.name: option.value for option in options}
        variation = {
            option.product_option: option for option in self.variable_options()
        }
        for option in options:
            if option not in variation:
                variation[option] = None
        return variation

    # def listing_options(self):
    #     """Return the product's listing product options as a dict."""
    #     return {
    #         option.product_option: option for option in self.selected_listing_options()
    #     }

    def variable_options(self):
        """Return list of Product Options which are variable for the range."""
        return VariationOptionValue.objects.filter(product=self).values_list(
            "name", "value"
        )

    def variation_values(self):
        """Return a list of the product's variation option values."""
        return VariationOptionValue.objects.filter(product=self).values_list(
            "value", flat=True
        )

    # def selected_listing_options(self):
    #     """Return list of Product Options which are listing options for the range."""
    #     options = self.product_range.listing_options()
    #     return self.product_options.filter(product_option__in=options).order_by(
    #         "product_option"
    #     )

    def stock_level(self):
        """Return the products current stock level in Cloud Commerce."""
        raise NotImplementedError()

    def name_extensions(self):
        """Return additions to the product name."""
        extensions = list(self.variation_values())
        if self.supplier_sku:
            extensions.append(self.supplier_sku)
        return extensions

    def update_stock_level(self, *, old, new):
        """Set the product's stock level in Cloud Commerce."""
        raise NotImplementedError()


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
    existing_skus = set(ProductRange.objects.values_list("sku", flat=True).distinct())
    return unique_sku(existing_skus=existing_skus, sku_function=generate_range_sku)
