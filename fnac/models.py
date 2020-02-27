"""Models for the fnac app."""

from django.db import models


class Category(models.Model):
    """Model for FNAC categories."""

    name = models.CharField(max_length=255, unique=True)
    english = models.TextField(unique=True)
    french = models.TextField(unique=True)

    def __str__(self):
        return self.name or self.english


class Size(models.Model):
    """Model for FNAC sizes."""

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class FnacRange(models.Model):
    """Model for FNAC product ranges."""

    name = models.CharField(max_length=255, unique=True)
    sku = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return f"{self.sku} - {self.name}"
