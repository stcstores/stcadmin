"""Model for suppliers."""

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Supplier(models.Model):
    """Model for suppliers."""

    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

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


class SupplierContact(models.Model):
    """Model for supplier contacts."""

    class Meta:
        """Meta class for Supplier."""

        verbose_name = "Supplier Contact"
        verbose_name_plural = "Supplier Contacts"
        ordering = ("name",)

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="supplier_contacts"
    )
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

    def save(self, *args, **kwargs):
        """Validate the instance and save it."""
        self.full_clean()
        return super().save(*args, **kwargs)
