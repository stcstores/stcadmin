"""Model for suppliers."""

from ccapi import CCAPI
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Supplier(models.Model):
    """Model for suppliers."""

    SUPPLIER_OPTION_ID = 35131

    name = models.CharField(max_length=200, unique=True)
    product_option_ID = models.CharField(max_length=20, unique=True)
    factory_ID = models.CharField(max_length=20, unique=True)
    inactive = models.BooleanField(default=False)

    class Meta:
        """Meta class for Supplier."""

        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Return the absolute URL for the supplier instance."""
        return reverse("inventory:supplier", kwargs={"pk": self.pk})

    @property
    def active(self):
        """Return True if the supplier is active, otherwise return False."""
        return not self.inactive

    def save(self, *args, **kwargs):
        """
        Create or update the Supplier object.

        Create a Product Option and Factory in Cloud Commerce if neither exist.
        """
        if self.product_option_ID == "" or self.factory_ID == "":
            self.product_option_ID = self.create_product_option(self.name)
            self.factory_ID = self.create_factory(self.name)
        super().save(*args, **kwargs)

    @classmethod
    def create_product_option(cls, name):
        """
        Return the ID of the Supplier Product Option matching name.

        If it does not exist it will be created.
        """
        return CCAPI.get_option_value_id(cls.SUPPLIER_OPTION_ID, name, create=True)

    @classmethod
    def create_factory(cls, name):
        """
        Return the ID of the Cloud Commerce Factory matching name.

        If it does not exist it will be created.
        """
        factories = CCAPI.get_factories()
        for factory in factories:
            if factory.name == name:
                return factory.id
        new_factory = CCAPI.create_factory(name)
        return new_factory.id


class SupplierContact(models.Model):
    """Model for supplier contacts."""

    class Meta:
        """Meta class for Supplier."""

        verbose_name = "Supplier Contact"
        verbose_name_plural = "Supplier Contacts"
        ordering = ("name",)

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        string = self.supplier.name
        if self.name is not None:
            string += f" - {self.name}"
        return string

    def get_absolute_url(self):
        """Return the absolute URL for the contact instance's supplier."""
        return self.supplier.get_absolute_url()

    def clean(self, *args, **kwargs):
        """Ensure at least one field is not empty."""
        super().clean(*args, **kwargs)
        if self.name is None and self.email is None and self.phone is None:
            raise ValidationError(
                "At least one of (name, email, phone) must not be empty"
            )
