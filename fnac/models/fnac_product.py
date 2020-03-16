"""Model for products."""

from django.db import models
from django.db.models import Q

from .fnac_range import FnacRange
from .size import Size


class FnacProductManager(models.Manager):
    """Model Manger for the FnacProduct model."""

    def to_be_created(self):
        """Return a queryset of products that have not been created or marked to not create."""
        return self.get_queryset().filter(created=False, do_not_create=False)

    def out_of_stock(self):
        """Return a queryset of out of stock products."""
        return self.to_be_created().filter(stock_level=0)

    def in_stock(self):
        """Return a queryset of in stock products."""
        return self.to_be_created().filter(stock_level__gt=0)

    def translated(self):
        """Return a queryset of products that have been translated."""
        return (
            self.to_be_created()
            .filter(
                Q(translation__isnull=False)
                & ~Q(translation__name="")
                & ~Q(translation__description="")
                & ~Q(~Q(colour="") & Q(translation__colour=""))
            )
            .difference(self.missing_inventory_information())
        )

    def not_translated(self):
        """Retrun a queryset of products that have not been translated."""
        return (
            self.to_be_created()
            .filter(
                Q(translation__isnull=True)
                | Q(translation__name="")
                | Q(translation__description="")
                | Q(~Q(colour="") & Q(translation__colour=""))
            )
            .difference(self.missing_inventory_information())
        )

    def barcode_valid(self):
        """Return a queryset of products with valid barcodes."""
        return self.to_be_created().exclude(barcode="")

    def barcode_invalid(self):
        """Return a queryset of products with valid barcodes."""
        return self.to_be_created().filter(barcode="")

    def has_image(self):
        """Return a queryset of products with at least one image."""
        return self.to_be_created().exclude(image_1="")

    def missing_image(self):
        """Return a queryset of products without an image."""
        return self.to_be_created().filter(image_1="")

    def size_valid(self):
        """Return a queryset of products with valid size information."""
        return self.to_be_created().exclude(
            ~Q(english_size="") & Q(french_size__isnull=True)
        )

    def size_invalid(self):
        """Return a queryset of products with invalid size information."""
        return self.to_be_created().filter(
            ~Q(english_size="") & Q(french_size__isnull=True)
        )

    def has_category(self):
        """Return a queryset of products with categories."""
        return self.to_be_created().filter(fnac_range__category__isnull=False)

    def missing_category(self):
        """Return a queryset of products without categories."""
        return self.to_be_created().filter(fnac_range__category__isnull=True)

    def has_price(self):
        """Return a queryset of products with prices."""
        return self.to_be_created().filter(price__isnull=False)

    def missing_price(self):
        """Return a queryset of products without a price."""
        return self.to_be_created().filter(price__isnull=True)

    def has_description(self):
        """Return a queryset of products with prices."""
        return self.to_be_created().exclude(description="")

    def missing_description(self):
        """Return a queryset of products without a price."""
        return self.to_be_created().filter(description="")

    def missing_inventory_information(self):
        """Return a queryset of products missing description, barcode or images."""
        return (
            self.missing_description() | self.barcode_invalid() | self.missing_image()
        )

    def ready_to_create(self):
        """Return a queryset of products that are ready to be listed on FNAC."""
        return (
            self.in_stock()
            & self.translated()
            & self.barcode_valid()
            & self.has_image()
            & self.size_valid()
            & self.has_category()
            & self.has_price()
            & self.has_description()
        )


class FnacProduct(models.Model):
    """Model for FNAC products."""

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, unique=True)
    fnac_range = models.ForeignKey(FnacRange, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=15)
    description = models.TextField()
    price = models.PositiveIntegerField(blank=True, null=True)
    brand = models.CharField(max_length=255)
    colour = models.CharField(max_length=255, blank=True)
    english_size = models.CharField(max_length=255, blank=True, null=True)
    french_size = models.ForeignKey(
        Size, on_delete=models.PROTECT, blank=True, null=True
    )
    stock_level = models.IntegerField()
    image_1 = models.CharField(max_length=20, blank=True)
    image_2 = models.CharField(max_length=20, blank=True)
    image_3 = models.CharField(max_length=20, blank=True)
    image_4 = models.CharField(max_length=20, blank=True)
    do_not_create = models.BooleanField(default=False)
    created = models.BooleanField(default=False)

    objects = FnacProductManager()

    def __str__(self):
        return f"{self.sku} - {self.name}"
