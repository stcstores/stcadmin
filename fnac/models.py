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


class FnacProduct(models.Model):
    """Model for FNAC products."""

    name = models.CharField(max_length=255, unique=True)
    sku = models.CharField(max_length=255, unique=True)
    fnac_range = models.ForeignKey(FnacRange, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=15)
    description = models.TextField()
    price = models.PositiveIntegerField()
    brand = models.CharField(max_length=255)
    colour = models.CharField(max_length=255)
    stock_level = models.IntegerField()
    do_not_create = models.BooleanField(default=False)
    created = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sku} - {self.name}"
