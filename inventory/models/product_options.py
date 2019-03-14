"""Model for departments."""

from ccapi import CCAPI
from django.db import models
from orderable.models import Orderable

from .locations import Bay, Warehouse


class BaseProductOptionModel(models.Model):
    """Abstract model for Cloud Commerce Product Options."""

    PRODUCT_OPTION_ID = None
    PRODUCT_OPTION_NAME = None

    name = models.CharField(max_length=50, unique=True)
    product_option_ID = models.CharField(max_length=20, unique=True)
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

    def save(self, *args, **kwargs):
        """Create or update the Department object.

        Create a Product Option in Cloud Commerce if self.product_option_ID is empty.
        """
        if self.product_option_ID == "":
            self.product_option_ID = self.create_product_option(self.name)
        super().save(*args, **kwargs)

    @classmethod
    def get_product_options(cls):
        """Return all Cloud Commerce Product Options for this model."""
        return CCAPI.get_product_options()[cls.PRODUCT_OPTION_NAME]

    @classmethod
    def create_product_option(cls, name):
        """
        Return the ID of the Department Product Option matching name.

        If it does not exist it will be created.
        """
        return CCAPI.get_option_value_id(cls.PRODUCT_OPTION_ID, name, create=True)


class OrderableProductOptionModel(Orderable, BaseProductOptionModel):
    """Orderable abstract model for product options."""

    class Meta(Orderable.Meta, BaseProductOptionModel.Meta):
        """Meata class for OrderableProductOptionModel."""

        abstract = True


class Department(BaseProductOptionModel):
    """Model for departments."""

    PRODUCT_OPTION_ID = 34325
    PRODUCT_OPTION_NAME = "Department"

    abriviation = models.CharField(max_length=3, blank=True, null=True)

    class Meta(BaseProductOptionModel.Meta):
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


class PackageType(OrderableProductOptionModel):
    """Model for package types."""

    PRODUCT_OPTION_ID = 33852
    PRODUCT_OPTION_NAME = "Package Type"

    class Meta(OrderableProductOptionModel.Meta):
        """Meta class for PackageType."""

        verbose_name = "Package Type"
        verbose_name_plural = "Package Types"


class InternationalShipping(OrderableProductOptionModel):
    """Model for international shipping."""

    PRODUCT_OPTION_ID = 37272
    PRODUCT_OPTION_NAME = "International Shipping"

    class Meta(OrderableProductOptionModel.Meta):
        """Meta class for InternationalShipping."""

        verbose_name = "International Shipping"
        verbose_name_plural = "International Shipping"
