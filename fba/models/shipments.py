"""Models for managing FBA shipments."""
import csv
import io

from django.db import models


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


class FBAShipmentPackage(models.Model):
    """Model for FBA Shipment packages."""

    order = models.ForeignKey(
        FBAShipmentOrder, related_name="shipment_package", on_delete=models.CASCADE
    )
    sku = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.SmallIntegerField()
    length_cm = models.SmallIntegerField()
    width_cm = models.SmallIntegerField()
    height_cm = models.SmallIntegerField()
    weight_kg = models.FloatField()
    value = models.SmallIntegerField(default=100)
    country_of_origin = models.CharField(max_length=255, default="United Kingdom")
    hr_code = models.CharField(max_length=255)

    class Meta:
        """Meta class for FBAShipmentPackage."""

        verbose_name = "FBA Shipment Package"
        verbose_name_plural = "FBA Shipment Packages"

    def __str__(self):
        return f"{self.order} package {self.sku}"


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
                row_data = cls._create_row_data(order=order, package=package)
                row = [row_data[header] for header in cls.HEADER]
                rows.append(row)
        return rows

    @classmethod
    def _create_row_data(cls, order, package):
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
            cls.LENGTH: package.length_cm,
            cls.WIDTH: package.width_cm,
            cls.HEIGHT: package.height_cm,
            cls.DESCRIPTION: package.description,
            cls.SKU: package.sku,
            cls.WEIGHT: package.weight_kg,
            cls.VALUE: str(float(package.value / 100)).format("{:2f}"),
            cls.QUANTITY: package.quantity,
            cls.COUNTRY_OF_ORIGIN: package.country_of_origin,
            cls.HR_CODE: package.hr_code,
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
