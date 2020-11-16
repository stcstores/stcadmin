"""Model for departments."""

from ccapi import CCAPI
from django.db import models

from .locations import Bay, Warehouse


class BaseProductOptionValueModel(models.Model):
    """Abstract model for Cloud Commerce Product Option Values."""

    product_option_value_ID = models.CharField(max_length=20, unique=True)

    class Meta:
        """Meta class for the BaseProductOptionModel abstract model."""

        abstract = True

    def save(self, *args, **kwargs):
        """Create or update the Department object.

        Create a Product Option in Cloud Commerce if self.product_option_value_ID is empty.
        """
        if self.product_option_value_ID == "":
            self.product_option_value_ID = self.create_CC_product_option(self.value)
        super().save(*args, **kwargs)

    @classmethod
    def get_product_options(cls):
        """Return all Cloud Commerce Product Options for this model."""
        return CCAPI.get_product_options()[cls.PRODUCT_OPTION_NAME]

    def create_CC_product_option(self, value):
        """
        Return the ID of the Department Product Option matching name.

        If it does not exist it will be created.
        """
        return CCAPI.create_option_value(self.product_option.product_option_ID, value)


class BaseNonListingProductOptionModel(BaseProductOptionValueModel):
    """Abstract model for Cloud Commerce Product Options."""

    PRODUCT_OPTION_ID = None
    PRODUCT_OPTION_NAME = None

    name = models.CharField(max_length=50, unique=True)
    inactive = models.BooleanField(default=False)

    class Meta:
        """Meta class for the BaseProductOptionModel abstract model."""

        abstract = True
        ordering = ("inactive", "name")

    def __str__(self):
        return self.name

    @property
    def active(self):
        """Return True if the department is active, otherwise return False."""
        return not self.inactive

    @property
    def value(self):
        """Return self.name for compatibility with BaseProductOptionValueModel."""
        return self.name

    @classmethod
    def create_CC_product_option(cls, value):
        """
        Return the ID of the Department Product Option matching name.

        If it does not exist it will be created.
        """
        return CCAPI.create_option_value(cls.PRODUCT_OPTION_ID, value)


class Department(BaseNonListingProductOptionModel):
    """Model for departments."""

    PRODUCT_OPTION_ID = 34325
    PRODUCT_OPTION_NAME = "Department"

    abriviation = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        """Meta class for Department."""

        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def default_warehouse(self):
        """Return the default warehouse for the department."""
        try:
            return Warehouse.objects.get(name=self.name)
        except Warehouse.DoesNotExist:
            return None

    def default_bay(self):
        """Return the default bay for the department."""
        try:
            return Bay.objects.get(name=self.name)
        except Bay.DoesNotExist:
            return None


class PackageType(BaseNonListingProductOptionModel):
    """Model for package types."""

    PRODUCT_OPTION_ID = 33852
    PRODUCT_OPTION_NAME = "Package Type"
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)

    large_letter_compatible = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        """Meta class for PackageType."""

        verbose_name = "Package Type"
        verbose_name_plural = "Package Types"
        ordering = ["ordering"]


class InternationalShipping(BaseNonListingProductOptionModel):
    """Model for international shipping."""

    PRODUCT_OPTION_ID = 37272
    PRODUCT_OPTION_NAME = "International Shipping"
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        """Meta class for InternationalShipping."""

        verbose_name = "International Shipping"
        verbose_name_plural = "International Shipping"
        ordering = ["ordering"]
