"""Models for managing FBA shipments."""
import csv
import io

from django.db import models

from .fba import FBAOrder


class FBAShipmentDestinationActiveManager(models.Manager):
    """Manager for active shipment destinations."""

    def get_queryset(self):
        """Return a queryset of shipment destinations that are enabled."""
        return super().get_queryset().filter(is_enabled=True)


class FBAShipmentDestination(models.Model):
    """Model for FBA Shipment desinations."""

    name = models.CharField(max_length=255, unique=True)
    is_enabled = models.BooleanField(default=True)
    recipient_last_name = models.CharField(max_length=255, default="STC FBA")
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    address_line_3 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postcode = models.CharField(max_length=255)

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
        return ITDShipmentFile().create(self)


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
    is_on_hold = models.BooleanField(default=False)

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


class FBAShipmentItem(models.Model):
    """Model for FBA Shipment items."""

    package = models.ForeignKey(
        FBAShipmentPackage, related_name="shipment_item", on_delete=models.CASCADE
    )
    sku = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.SmallIntegerField()
    weight_kg = models.FloatField()
    value = models.SmallIntegerField(default=100)
    country_of_origin = models.CharField(max_length=255, default="United Kingdom")
    hr_code = models.CharField(max_length=255)

    class Meta:
        """Meta class for FBAShipmentItem."""

        verbose_name = "FBA Shipment Item"
        verbose_name_plural = "FBA Shipment Items"

    def __str__(self):
        return f"{self.shipment_order} package {self.package.package_number()} - {self.sku}"


class ITDShipmentFile:
    """ITD Shipment file generator."""

    LAST_NAME = "Recipient Last Name"
    ADDRESS_1 = "Ship to Address 1"
    ADDRESS_2 = "Ship to Address 2"
    ADDRESS_3 = "Ship to Address 3"
    CITY = "Ship to City"
    STATE = "Ship to State"
    COUNTRY = "Ship to Country"
    POSTCODE = "Ship to Zip/Postcode"
    ORDER_NUMBER = "Order Number"
    PACKAGE_NUMBER = "Package Number"
    LENGTH = "Package Length"
    WIDTH = "Package Width"
    HEIGHT = "Package Height"
    DESCRIPTION = "Package Item Description"
    SKU = "Package Item SKU"
    WEIGHT = "Package Item Weight"
    VALUE = "Package Item Value"
    QUANTITY = "Package Item Quantity"
    COUNTRY_OF_ORIGIN = "Package Item Country of Origin"
    HR_CODE = "Package Item Harmonisation Code"
    SHIPMENT_METHOD = "Order Shipment Method"

    HEADER = [
        LAST_NAME,
        ADDRESS_1,
        ADDRESS_2,
        ADDRESS_3,
        CITY,
        STATE,
        COUNTRY,
        POSTCODE,
        ORDER_NUMBER,
        PACKAGE_NUMBER,
        LENGTH,
        WIDTH,
        HEIGHT,
        DESCRIPTION,
        SKU,
        WEIGHT,
        VALUE,
        QUANTITY,
        COUNTRY_OF_ORIGIN,
        HR_CODE,
        SHIPMENT_METHOD,
    ]

    @classmethod
    def _create_rows(cls, shipment_export):
        rows = []
        for order in shipment_export.shipment_order.all():
            for package in order.shipment_package.all():
                for item in package.shipment_item.all():
                    row_data = cls._create_row_data(
                        shipment_order=order, package=package, item=item
                    )
                    row = [row_data[header] for header in cls.HEADER]
                    rows.append(row)
        return rows

    @classmethod
    def _create_row_data(cls, order, package, item):
        row_data = {
            cls.LAST_NAME: order.destination.recipient_last_name,
            cls.ADDRESS_1: order.destination.address_line_1,
            cls.ADDRESS_2: order.destination.address_line_2,
            cls.ADDRESS_3: order.destination.address_line_3,
            cls.CITY: order.destination.city,
            cls.STATE: order.destination.state,
            cls.COUNTRY: order.destination.country,
            cls.POSTCODE: order.destination.postcode,
            cls.ORDER_NUMBER: order.order_number(),
            cls.PACKAGE_NUMBER: package.package_number(),
            cls.LENGTH: package.length_cm,
            cls.WIDTH: package.width_cm,
            cls.HEIGHT: package.height_cm,
            cls.DESCRIPTION: item.description,
            cls.SKU: item.sku,
            cls.WEIGHT: item.weight_kg,
            cls.VALUE: str(float(item.value / 100)).format("{:2f}"),
            cls.QUANTITY: item.quantity,
            cls.COUNTRY_OF_ORIGIN: item.country_of_origin,
            cls.HR_CODE: item.hr_code,
            cls.SHIPMENT_METHOD: order.shipment_method.identifier,
        }
        return row_data

    @classmethod
    def create(cls, shipment_export):
        """Generate a shipment file for the orders associated with an export."""
        rows = cls._create_rows(shipment_export)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(cls.HEADER)
        for row in rows:
            writer.writerow(row)
        return output.getvalue()
