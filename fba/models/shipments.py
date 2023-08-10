"""Models for managing FBA shipments."""


from django.conf import settings
from django.db import models
from solo.models import SingletonModel

from .fba import FBAOrder
from .shipment_files import UPSAddressFile, UPSShipmentFile


def shortened_description(desc, max_length=30):
    """Return a shortened description."""
    if desc is None:
        return ""
    return desc[:max_length] + "..." if len(desc) > max_length else desc


def shortened_description_list(descriptions, max_length=30):
    """Return a shortened description from a list of descriptions."""
    descriptions = list(set(descriptions))
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
    contact_telephone = models.CharField(max_length=20, null=True)
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


class FBAShipmentExport(models.Model):
    """Model for FBA Shipment exports."""

    created_at = models.DateTimeField(auto_now_add=True)

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

    def description(self):
        """Return a description of the shipments contained in the export."""
        return "\n".join(
            [shipment.description() for shipment in self.shipment_order.all()]
        )

    def order_numbers(self):
        """Return the order numbers of the shipments contained in the export."""
        return "\n".join(
            [shipment.order_number() for shipment in self.shipment_order.all()]
        )

    def destinations(self):
        """Return the destinations of the shipments contained in the export."""
        return "\n".join(
            [shipment.destination.name for shipment in self.shipment_order.all()]
        )

    def shipment_count(self):
        """Return the number of shipments contained in the export."""
        return self.shipment_order.count()

    def package_count(self):
        """Return the number of packages in the export."""
        return sum(
            (
                shipment.shipment_package.count()
                for shipment in self.shipment_order.all()
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


class FBAShipmentOrderManager(models.Manager):
    """Manager for FBA Shipment Orders."""


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

    objects = FBAShipmentOrderManager()

    class Meta:
        """Meta class for FBAShipmentOrder."""

        verbose_name = "FBA Shipment Order"
        verbose_name_plural = "FBA Shipment Orders"

    def order_number(self):
        """Return a generated order number for the order."""
        number = str(self.pk).zfill(5)
        return f"STC_FBA_{number}"

    def __str__(self):
        return f"FBA Shipment Order {self.order_number()}"

    def weight_kg(self):
        """Return the total weight of the shipment."""
        return self.shipment_package.aggregate(models.Sum("shipment_item__weight_kg"))[
            "shipment_item__weight_kg__sum"
        ]

    def value(self):
        """Return the total value of the shipment."""
        return self.shipment_package.aggregate(models.Sum("shipment_item__value"))[
            "shipment_item__value__sum"
        ]

    def item_count(self):
        """Return the total number of items in the shipment."""
        return self.shipment_package.aggregate(models.Sum("shipment_item__quantity"))[
            "shipment_item__quantity__sum"
        ]

    def description(self, max_length=30):
        """Return a text description of the shipment."""
        descriptions = self.shipment_package.values_list(
            "shipment_item__description", flat=True
        )
        return shortened_description_list(descriptions, max_length=max_length)

    def is_shipable(self):
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


class FBAShipmentPackage(models.Model):
    """Model for FBA Shipment packages."""

    shipment_order = models.ForeignKey(
        FBAShipmentOrder, related_name="shipment_package", on_delete=models.CASCADE
    )
    fba_order = models.ForeignKey(
        FBAOrder,
        related_name="shipment_package",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    length_cm = models.SmallIntegerField()
    width_cm = models.SmallIntegerField()
    height_cm = models.SmallIntegerField()

    class Meta:
        """Meta class for FBAShipmentPackage."""

        verbose_name = "FBA Shipment Package"
        verbose_name_plural = "FBA Shipment Packages"

    def __str__(self):
        return f"{self.shipment_order} - {self.package_number()}"

    def package_number(self):
        """Return a package number for the package."""
        return f"{self.shipment_order.order_number()}_{self.pk}"

    def weight_kg(self):
        """Return the total weight of the package."""
        return self.shipment_item.aggregate(weight=models.Sum("weight_kg"))["weight"]

    def value(self):
        """Return the total value of the package."""
        return self.shipment_item.aggregate(value=models.Sum("value"))["value"]

    def description(self, max_length=30):
        """Return a description string for the package."""
        descriptions = self.shipment_item.values_list("description", flat=True)
        return shortened_description_list(descriptions, max_length=max_length)

    def customs_declaration(self, max_length=35):
        """Return a customs delcaration string."""
        descriptions = self.shipment_item.values_list("description", flat=True)
        return ", ".join(descriptions)[:max_length]


class FBAShipmentItem(models.Model):
    """Model for FBA Shipment items."""

    package = models.ForeignKey(
        FBAShipmentPackage, related_name="shipment_item", on_delete=models.CASCADE
    )
    sku = models.CharField(max_length=255, verbose_name="SKU")
    description = models.TextField()
    quantity = models.SmallIntegerField()
    weight_kg = models.FloatField(verbose_name="Weight (kg)")
    value = models.SmallIntegerField(default=100)
    country_of_origin = models.CharField(
        max_length=255, default="United Kingdom", verbose_name="Country of Origin"
    )
    hr_code = models.CharField(max_length=255, verbose_name="HR Code")

    class Meta:
        """Meta class for FBAShipmentItem."""

        verbose_name = "FBA Shipment Item"
        verbose_name_plural = "FBA Shipment Items"

    def __str__(self):
        return f"{self.package.shipment_order} package {self.package.package_number()} - {self.sku}"

    def short_description(self, max_length=30):
        """Return a shortended description."""
        return shortened_description(self.description, max_length=max_length)
