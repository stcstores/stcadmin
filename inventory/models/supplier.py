"""Model for suppliers."""

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class SupplierQueryset(models.QuerySet):
    """Queryset for the Supplier model."""

    def active(self):
        """Return a queryset of suppliers that are active and not blacklisted."""
        return self.filter(active=True, blacklisted=False)

    def inactive(self):
        """Return a queryset of suppliers that are not active or blacklisted."""
        return self.filter(active=False, blacklisted=False)

    def blacklisted(self):
        """Return a queryset of suppliers that have been blacklisted."""
        return self.filter(blacklisted=True)


class SupplierManager(models.Manager):
    """Model manager for the Supplier model."""

    def get_queryset(self):
        """Return a supplier queryset."""
        return SupplierQueryset(self.model, using=self._db)

    def active(self):
        """Return a queryset of suppliers that are active and not blacklisted."""
        return self.get_queryset().active()

    def inactive(self):
        """Return a queryset of suppliers that are not active or blacklisted."""
        return self.get_queryset().inactive()

    def blacklisted(self):
        """Return a queryset of suppliers that have been blacklisted."""
        return self.get_queryset().blacklisted()


class Supplier(models.Model):
    """Model for suppliers."""

    name = models.CharField(max_length=50, unique=True, db_index=True)
    active = models.BooleanField(default=True)
    blacklisted = models.BooleanField(default=False)
    last_ordered_from = models.DateField(blank=True, null=True)
    restock_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    objects = SupplierManager()

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
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return f"{self.name} - {self.supplier.name}"
        else:
            return self.supplier.name

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
