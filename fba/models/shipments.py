"""Models for managing FBA shipments."""

from django.conf import settings
from django.db import models
from django.db.models import Case, Count, F, Sum, Value, When
from django.db.models.functions import Concat, Left, Length
from django.utils import timezone
from solo.models import SingletonModel

from .shipment_files import UPSAddressFile, UPSShipmentFile


def shortened_description(desc, max_length=30):
    """Return a shortened description."""
    if desc is None:
        return ""
    return desc[: max_length - 3] + "..." if len(desc) > max_length else desc


def shortened_description_list(descriptions, max_length=30):
    """Return a shortened description from a list of descriptions."""
    descriptions = sorted(set(descriptions))
    if len(descriptions) == 0:
        return ""
    description_text = shortened_description(descriptions[0], max_length=max_length)
    description = (
        f"{description_text} + {len(descriptions) - 1} other items"
        if len(descriptions) > 1
        else description_text
    )
    return description


class ShipmentConfig(SingletonModel):
    """Model for storing FBA Shipment settings."""

    token = models.CharField(max_length=128)

    class Meta:
        """Meta class for ShipmentConfig."""

        verbose_name = "Shipment Config"


class FBAShipmentDestinationActiveManager(models.Manager):
    """Manager for active shipment destinations."""

    def get_queryset(self):
        """Return a queryset of shipment destinations that are enabled."""
        return super().get_queryset().filter(is_enabled=True)


class FBAShipmentDestination(models.Model):
    """Model for FBA Shipment desinations."""

    name = models.CharField(max_length=255, unique=True)
    recipient_name = models.CharField(max_length=255, default="STC FBA")
    contact_telephone = models.CharField(max_length=50, null=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    address_line_3 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    country_iso = models.CharField(max_length=2, null=True)
    postcode = models.CharField(max_length=255)

    is_enabled = models.BooleanField(default=True)

    objects = models.Manager()
    active = FBAShipmentDestinationActiveManager()

    class Meta:
        """Meta class for FBAShipmentDestination."""

        verbose_name = "FBA Shipment Destination"
        verbose_name_plural = "FBA Shipment Destinations"
        ordering = ("name",)

    def __repr__(self):
        return f"<FBAShipmentDestination: {self.name}>"

    def __str__(self):
        return self.name


class FBAShipmentExportManager(models.Manager):
    """Model manager for the FBAShipment Export model."""

    def get_queryset(self):
        """Annotate queryset."""
        return (
            super()
            .get_queryset()
            .annotate(
                shipment_count=Count("shipment_order", distinct=True),
                package_count=Count("shipment_order__shipment_package", distinct=True),
            )
        )


class FBAShipmentMethod(models.Model):
    """View for FBA Shipment methods."""

    name = models.CharField(max_length=255, unique=True)
    identifier = models.CharField(max_length=255)
    priority = models.SmallIntegerField(default=0)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        """Meta class for FBAShipmentMethod."""

        verbose_name = "FBA Shipment Method"
        verbose_name_plural = "FBA Shipment Methods"
        ordering = ("priority",)

    def __str__(self):
        return self.name


class FBAShipmentExport(models.Model):
    """Model for FBA Shipment exports."""

    created_at = models.DateTimeField(default=timezone.now)

    objects = FBAShipmentExportManager()

    class Meta:
        """Meta class for FBAShipmentExport."""

        verbose_name = "FBA Shipment Export"
        verbose_name_plural = "FBA Shipment Exports"
        ordering = ("-created_at",)

    def __str__(self):
        return f"FBA Shipment Export {self.created_at.strftime('%Y-%m-%d')}"

    def generate_export_file(self):
        """Return an FBA Shipment .csv."""
        return UPSShipmentFile().create(self)

    def generate_address_file(self):
        """Return a UPS Address .csv."""
        return UPSAddressFile.create(self)

    def order_numbers(self):
        """Return the order numbers of the shipments contained in the export."""
        numbers = []
        for shipment in self.shipment_order.all():
            numbers.append(shipment.order_number)
        return sorted(numbers)

    def destinations(self):
        """Return the destinations of the shipments contained in the export."""
        return self.shipment_order.values_list(
            "destination__name", flat=True
        ).distinct()


class FBAShipmentOrderManager(models.Manager):
    """Model Manager for the FBAShipmentOrder model."""

    def get_queryset(self):
        """Annotate queryset."""
        return (
            super()
            .get_queryset()
            .annotate(
                weight_kg=Sum(
                    F("shipment_package__shipment_item__weight_kg")
                    * F("shipment_package__shipment_item__quantity")
                ),
                value=Sum(
                    F("shipment_package__shipment_item__value")
                    * F("shipment_package__shipment_item__quantity")
                ),
                item_count=Sum("shipment_package__shipment_item__quantity"),
            )
        )


class FBAShipmentOrder(models.Model):
    """View for FBA Shipment orders."""

    export = models.ForeignKey(
        FBAShipmentExport,
        blank=True,
        null=True,
        related_name="shipment_order",
        on_delete=models.CASCADE,
    )
    destination = models.ForeignKey(FBAShipmentDestination, on_delete=models.PROTECT)
    shipment_method = models.ForeignKey(FBAShipmentMethod, on_delete=models.PROTECT)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=False,
        on_delete=models.PROTECT,
        related_name="fba_shipments",
    )
    is_on_hold = models.BooleanField(default=False)
    planned_shipment_date = models.DateField(blank=True, null=True)
    at_risk = models.BooleanField(default=False)

    objects = FBAShipmentOrderManager()

    class Meta:
        """Meta class for FBAShipmentOrder."""

        verbose_name = "FBA Shipment Order"
        verbose_name_plural = "FBA Shipment Orders"

    def __str__(self):
        return f"FBA Shipment Order {self.order_number}"

    @property
    def order_number(self):
        """Return the order's order number."""
        return f"STC_FBA_{str(self.pk).zfill(5)}"

    @property
    def description(self, max_length=30):
        """Return a text description of the shipment."""
        descriptions = self.shipment_package.values_list(
            "shipment_item__description", flat=True
        )
        return shortened_description_list(descriptions, max_length=max_length)

    @property
    def is_shippable(self):
        """Return True if shipment is ready for completion, otherwise False."""
        return all(
            (
                self.export is None,
                self.is_on_hold is False,
                self.shipment_package.count() > 0,
            )
        )

    def close_shipment_order(self):
        """Create a shipment export for this order."""
        export = FBAShipmentExport.objects.create()
        self.export = export
        self.save()
        return export


class FBAShipmentPackageManager(models.Manager):
    """Model Manager for the FBAShipmentPackage model."""

    def get_queryset(self):
        """Annotate queryset."""
        return (
            super()
            .get_queryset()
            .annotate(
                value=Sum(F("shipment_item__value") * F("shipment_item__quantity")),
                weight_kg=Sum(
                    F("shipment_item__weight_kg") * F("shipment_item__quantity")
                ),
            )
        )


class FBAShipmentPackage(models.Model):
    """Model for FBA Shipment packages."""

    shipment_order = models.ForeignKey(
        FBAShipmentOrder, related_name="shipment_package", on_delete=models.CASCADE
    )
    length_cm = models.PositiveIntegerField()
    width_cm = models.PositiveIntegerField()
    height_cm = models.PositiveIntegerField()

    objects = FBAShipmentPackageManager()

    class Meta:
        """Meta class for FBAShipmentPackage."""

        verbose_name = "FBA Shipment Package"
        verbose_name_plural = "FBA Shipment Packages"

    def __str__(self):
        return f"{self.shipment_order} - {self.package_number}"

    @property
    def package_number(self):
        """Return the package's package number."""
        return f"STC_FBA_{str(self.shipment_order.pk).zfill(5)}_{self.pk}"

    def description(self, max_length=30):
        """Return a description string for the package."""
        descriptions = self.shipment_item.values_list("description", flat=True)
        return shortened_description_list(descriptions, max_length=max_length)


class FBAShipmentItemManager(models.Manager):
    """Model manager for the FBAShipmentItem model."""

    def get_queryset(self):
        """Annotate queryset."""
        return (
            super()
            .get_queryset()
            .annotate(
                description_length=Length("description"),
                short_description=Case(
                    When(
                        description_length__gte=33,
                        then=Concat(Left(F("description"), 30), Value("...")),
                    ),
                    default=F("description"),
                    output_field=models.CharField(),
                ),
            )
        )


class FBAShipmentItem(models.Model):
    """Model for FBA Shipment items."""

    package = models.ForeignKey(
        FBAShipmentPackage, related_name="shipment_item", on_delete=models.CASCADE
    )
    sku = models.CharField(max_length=255, verbose_name="SKU")
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    weight_kg = models.FloatField(verbose_name="Weight (kg)")
    value = models.PositiveIntegerField(default=100)
    country_of_origin = models.CharField(
        max_length=255, default="United Kingdom", verbose_name="Country of Origin"
    )
    hr_code = models.CharField(max_length=255, verbose_name="HR Code")

    objects = FBAShipmentItemManager()

    class Meta:
        """Meta class for FBAShipmentItem."""

        verbose_name = "FBA Shipment Item"
        verbose_name_plural = "FBA Shipment Items"

    def __str__(self):
        return (
            f"{self.package.shipment_order} package {self.package.package_number}"
            f" - {self.sku}"
        )
