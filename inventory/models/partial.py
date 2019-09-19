"""Models for products."""

import itertools
import random
import string

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

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
from .products import (
    BaseProductModel,
    BaseProductRangeModel,
    Product,
    ProductOptionValueLink,
    ProductRange,
    ProductRangeSelectedOption,
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
        remaining_attempts -= 1
        if remaining_attempts == 0:
            raise Exception(
                f"Did not generate a unique SKU in {UNIQUE_SKU_ATTEMPTS} attemtps."
            )


class PartialProductRange(BaseProductRangeModel, models.Model):
    """Model for Product Ranges."""

    original_range = models.ForeignKey(
        ProductRange, on_delete=models.CASCADE, null=True
    )
    range_ID = models.CharField(max_length=50, unique=True, null=True)
    SKU = models.CharField(max_length=15, unique=True, db_index=True, null=True)
    name = models.CharField(max_length=255, null=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True)
    description = models.TextField(blank=True, default="")
    product_options = models.ManyToManyField(
        ProductOption, blank=True, through="PartialProductRangeSelectedOption"
    )
    amazon_search_terms = models.TextField(blank=True, default="")
    amazon_bullet_points = models.TextField(blank=True, default="")
    end_of_line = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    class Meta:
        """Meta class for partial Product Ranges."""

        verbose_name = "Partial Product Range"
        verbose_name_plural = "Partial Product Ranges"

    def __init__(self, *args, **kwargs):
        """Set foreign models."""
        self._selected_options_model = PartialProductRangeSelectedOption
        self._product_option_link_model = PartialProductOptionValueLink
        super().__init__(*args, **kwargs)

    @classmethod
    def get_new_SKU(cls):
        """Return an unused Range SKU."""
        existing_SKUs = cls._base_manager.values_list("SKU", flat=True)
        return unique_SKU(existing_SKUs, cls.generate_SKU)

    @staticmethod
    def generate_SKU():
        """Return a Product Range SKU."""
        return f"RNG_{generate_SKU()}"

    def product_count(self):
        """Return the number of products in this Range."""
        return self.partialproduct_set.count()

    def products(self):
        """Return a queryset of the Product Range's products."""
        return self.partialproduct_set.all().order_by("range_order", "id")

    @classmethod
    def copy_range(cls, product_range):
        """Return a PartialRange with PartialProducts matching this range."""
        range_data = ProductRange.objects.filter(pk=product_range.pk).values()[0]
        partial_range = PartialProductRange(**range_data)
        partial_range.save()
        range_selected_options = ProductRangeSelectedOption.objects.filter(
            product_range=product_range
        )
        for link in range_selected_options:
            PartialProductRangeSelectedOption(
                product_range=partial_range,
                product_option=link.product_option,
                variation=link.variation,
                pre_existing=True,
            ).save()
        for product_data in Product.objects.filter(
            product_range=product_range
        ).values():
            product_data["product_range"] = partial_range
            product_data["pre_existing"] = True
            product = PartialProduct(**product_data)
            product.save()
            links = ProductOptionValueLink.objects.filter(product=product_data["id"])
            for link in links:
                partial_link = PartialProductOptionValueLink(
                    product=product, product_option_value=link.product_option_value
                )
                partial_link.save()
            product.bays.set(Product.objects.get(id=product_data["id"]).bays.all())
        return partial_range

    def _variations(self):
        return [_.variation() for _ in self.products()]

    def has_missing_product_option_values(self):
        """Return True if any product is missing a variation product option value."""
        for option in self.product_options.all():
            for product in self.products():
                if not PartialProductOptionValueLink.objects.filter(
                    product=product, product_option_value__product_option=option
                ).exists():
                    return True
        return False

    def all_unique_variations(self, variations=None):
        """Return True if all the ranges products have unique variation options."""
        if variations is None:
            variations = self._variations()
        for a, b in itertools.combinations(variations, 2):
            if a == b:
                return False
        return True

    def product_options_have_multiple_values(self, variations=None):
        """Return True if every variation product option has at least two values."""
        if variations is None:
            variations = self._variations()
        for key in variations[0].keys():
            if all((_[key] == variations[0][key] for _ in variations)):
                return False
        return True

    def valid_variations(self):
        """Return True if all the ranges products have valid variation options."""
        variations = self._variations()
        if not self.product_options_have_multiple_values(variations):
            return False
        if self.has_missing_product_option_values():
            return False
        if not self.all_unique_variations(variations):
            return False
        return True

    def range_wide_values(self):
        """Return a dict of field values that are the same across the range."""
        data = PartialProduct.objects.filter(product_range=self).values()
        ignore_keys = (
            "original_product_id",
            "product_range_id",
            "pre_existing",
            "date_created",
            "status",
            "barcode",
            "range_order",
            "end_of_line",
            "multipack",
        )
        keys = []
        for key in data[0].keys():
            if len(set((data[_][key] for _ in range(len(data))))) == 1:
                keys.append(key)
        return {k: v for k, v in data[0].items() if k not in ignore_keys and k in keys}

    def pre_existing_options(self):
        """Return the product options that exist on the original product range."""
        link_IDs = PartialProductRangeSelectedOption.objects.filter(
            product_range=self, pre_existing=True
        ).values_list("product_option")
        return ProductOption.objects.filter(id__in=link_IDs)


class PartialProduct(BaseProductModel, models.Model):
    """Model for inventory products."""

    product_ID = models.CharField(max_length=50, unique=True, null=True)
    original_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    product_range = models.ForeignKey(PartialProductRange, on_delete=models.CASCADE)
    SKU = models.CharField(max_length=255, unique=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    supplier_SKU = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=20, null=True)
    purchase_price = models.DecimalField(decimal_places=2, max_digits=8, null=True)
    VAT_rate = models.ForeignKey(VATRate, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=8, null=True)
    retail_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True
    )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, null=True)
    package_type = models.ForeignKey(PackageType, on_delete=models.CASCADE, null=True)
    international_shipping = models.ForeignKey(
        InternationalShipping, on_delete=models.CASCADE, null=True
    )
    bays = models.ManyToManyField(Bay, blank=True)
    weight_grams = models.PositiveSmallIntegerField(null=True)
    length_mm = models.PositiveSmallIntegerField(null=True)
    height_mm = models.PositiveSmallIntegerField(null=True)
    width_mm = models.PositiveSmallIntegerField(null=True)
    product_options = models.ManyToManyField(
        ProductOptionValue, blank=True, through="PartialProductOptionValueLink"
    )
    multipack = models.BooleanField(default=False)
    end_of_line = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)
    gender = models.ForeignKey(Gender, null=True, blank=True, on_delete=models.SET_NULL)
    range_order = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=BaseProductModel.STATUS_CHOICES,
        default=BaseProductModel.CREATING,
    )
    date_created = models.DateField(auto_now_add=True)
    pre_existing = models.BooleanField(default=False)

    class Meta:
        """Meta class for Products."""

        verbose_name = "Partial Product"
        verbose_name_plural = "Partial Products"

    @classmethod
    def get_new_SKU(cls):
        """Return an unused Range SKU."""
        existing_SKUs = cls._base_manager.values_list("SKU", flat=True)
        return unique_SKU(existing_SKUs, cls.generate_SKU)

    @staticmethod
    def generate_SKU():
        """Return a Product SKU."""
        return generate_SKU()

    def is_complete(self):
        """Return True if the product is valid and complete, otherwise return False."""
        not_none_fields = (
            self.SKU,
            self.barcode,
            self.supplier,
            self.purchase_price,
            self.VAT_rate,
            self.price,
            self.brand,
            self.manufacturer,
            self.package_type,
            self.international_shipping,
            self.weight_grams,
        )
        if None in not_none_fields:
            return False
        return True


class PartialProductRangeSelectedOption(models.Model):
    """Model for linking Product Ranges to Product Options."""

    product_range = models.ForeignKey(PartialProductRange, on_delete=models.CASCADE)
    product_option = models.ForeignKey(ProductOption, on_delete=models.CASCADE)
    variation = models.BooleanField()
    pre_existing = models.BooleanField(default=False)

    class Meta:
        """Meta class for ProductRangeVariableOption."""

        verbose_name = "Partial Product Range Selected Option"
        verbose_name_plural = "Partial Product Range Selected Options"
        ordering = ("product_option",)
        unique_together = ("product_range", "product_option")

    def __str__(self):
        return (
            f"ProductRangeVariableOption: {self.product_range.SKU} - "
            f"{self.product_option.name}"
        )


class PartialProductOptionValueLink(models.Model):
    """Meta class for ProductRangeVariableOptions."""

    product = models.ForeignKey(PartialProduct, on_delete=models.CASCADE)
    product_option_value = models.ForeignKey(
        ProductOptionValue, on_delete=models.CASCADE
    )

    class Meta:
        """Meta class for PartialProductOptionValueLink."""

        verbose_name = "Partial Product Option Value Link"
        verbose_name_plural = "Partial Product Option Value Links"
        ordering = ("product_option_value__product_option",)
        unique_together = ("product", "product_option_value")

    def __str__(self):
        return (
            f"PartialProductOptionValueLink: {self.product.SKU} - "
            f"{self.product_option_value.value}"
        )


class ProductEdit(models.Model):
    """Model for storing in progress product edits."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_range = models.OneToOneField(
        ProductRange, on_delete=models.CASCADE, null=True
    )
    partial_product_range = models.OneToOneField(
        PartialProductRange, on_delete=models.CASCADE
    )
    product_option_values = models.ManyToManyField(ProductOptionValue)

    class Meta:
        """Meta class for ProductEdit."""

        verbose_name = "Product Edit"
        verbose_name_plural = "Product Edits"

    def __str__(self):
        return str(self.partial_product_range)

    def variation_options(self):
        """Return a dict of {product_option: list(values)} for the product range."""
        selected_product_options = self.partial_product_range.variation_options()
        variation_options = {option: [] for option in selected_product_options}
        for option in selected_product_options:
            variation_options[option] = list(
                self.product_option_values.filter(product_option=option)
            )
        return variation_options

    @transaction.atomic
    def create_product(self, options):
        """Create the new partial product."""
        product_data = self.partial_product_range.range_wide_values()
        product_data["id"] = None
        product_data["product_range"] = self.partial_product_range
        product_data["SKU"] = PartialProduct.get_new_SKU()
        product_data["date_created"] = timezone.now()
        product = PartialProduct(**product_data)
        product.save()
        for option in options:
            PartialProductOptionValueLink(
                product=product, product_option_value=option
            ).save()
        return product

    def delete(self, *args, **kwargs):
        """Delete the product edit and associated products."""
        self.partial_product_range.delete()
        super().delete(*args, **kwargs)

    @classmethod
    @transaction.atomic
    def create_product_edit(cls, user, product_range):
        """Create a product edit."""
        partial_product_range = PartialProductRange.copy_range(product_range)
        edit = cls._default_manager.create(
            product_range=product_range,
            partial_product_range=partial_product_range,
            user=user,
        )
        option_values = [
            _.product_option_value
            for _ in ProductOptionValueLink.objects.filter(
                product__product_range=product_range
            )
        ]
        for value in option_values:
            edit.product_option_values.add(value)
        return edit
