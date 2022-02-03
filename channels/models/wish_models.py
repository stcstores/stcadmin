"""Models for managing the Wish channel."""

import csv
import io
from dataclasses import dataclass

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.utils import timezone
from file_exchange.models import FileDownload, FileDownloadManager

from orders.models import Order as CloudCommerceOrder

from .cloud_commerce_order import CreatedOrder


class WishImport(models.Model):
    """Model for Wish order imports."""

    created_at = models.DateTimeField(auto_now_add=True)


class WishOrder(models.Model):
    """Model for imported Wish orders."""

    wish_import = models.ForeignKey(WishImport, on_delete=models.CASCADE)
    wish_transaction_id = models.CharField(max_length=255)
    wish_order_id = models.CharField(max_length=255)
    order = models.ForeignKey(
        CreatedOrder, blank=True, null=True, on_delete=models.PROTECT
    )
    error = models.TextField(blank=True)
    fulfiled = models.BooleanField(default=False)
    fulfilment_export = models.ForeignKey(
        "WishBulkFulfilmentExport", blank=True, null=True, on_delete=models.SET_NULL
    )

    def is_on_fulfilment_export(self):
        """Return True if the order is included in a fulfilment export, othwise False."""
        return bool(self.fulfilment_export)


@dataclass
class ExportOrder:
    """Dataclass holding a WishOrder and matching Cloud Commerce order."""

    wish_order: WishOrder
    cloud_commerce_order: CloudCommerceOrder


class WishBulkfulfilExportManager(FileDownloadManager):
    """Manager for the channels.WishBulkFulfilmentExport model."""

    @classmethod
    def _get_orders(cls):
        """Return a list of EportOrder for orders awaiting fulfillment."""
        wish_orders = WishOrder.objects.filter(
            order__isnull=False, fulfiled=False, fulfilment_export__isnull=True
        )
        order_ids = wish_orders.values_list("order__order_id", flat=True)
        cc_orders = CloudCommerceOrder.objects.filter(
            order_ID__in=order_ids, dispatched_at__isnull=False
        )
        order_match = {order.order.order_id: order for order in wish_orders}
        orders = [
            ExportOrder(
                wish_order=order_match[cc_order.order_ID], cloud_commerce_order=cc_order
            )
            for cc_order in cc_orders
        ]
        return orders


class WishBulkFulfilmentExport(FileDownload):
    """Model for Wish Bulk Filfilment export files."""

    download_file = models.FileField(
        blank=True, null=True, upload_to="channels/wish/wish_fulfilment_files"
    )

    objects = WishBulkfulfilExportManager()

    def generate_file(self):
        """Create an export file."""
        filename = f"wish_bulk_filfillment_{timezone.now().strftime('%Y-%m-%d')}.csv"
        self.orders = WishBulkfulfilExportManager._get_orders()
        if len(self.orders) == 0:
            raise Exception("No orders to export")
        contents = WishBulkfulfilFile.generate_file(self.orders)
        return SimpleUploadedFile(name=filename, content=contents.encode("utf-8"))

    def post_generation(self):
        """Add orders to the export."""
        for order in self.orders:
            order.wish_order.fulfilment_export = self
            order.wish_order.fulfiled = True
            order.wish_order.save()

    def get_download_link(self):
        """Return a link to the download file or an empty string."""
        if self.download_file:
            return self.download_file.url
        else:
            return ""


class WishBulkfulfilFile:
    """Class for generating Wish Order Fulfilment Files."""

    SHIPPING_PROVIDER = "Shipping Provider"
    ORIGIN_COUNTRY_CODE = "Origin Country Code"
    ORDER_ID = "Order Id"
    TRACKING_NUMBER = "Tracking Number"
    SHIP_NOTE = "Ship Note"

    DEFAULT_ORIGIN_CODE = "GB"
    DEFAULT_SHIPPING_PROVIDER = "N/A"

    HEADER = [
        SHIPPING_PROVIDER,
        ORIGIN_COUNTRY_CODE,
        ORDER_ID,
        TRACKING_NUMBER,
        SHIP_NOTE,
    ]

    SHIPPING_PROVIDER_NAME_OVERRIDES = {"Landmark": "LandmarkGlobal"}

    @classmethod
    def create_rows(cls, orders):
        """Return a list of rows to be included in the .csv."""
        rows = []
        for order in orders:
            row = cls.create_row(
                cc_order=order.cloud_commerce_order, wish_order=order.wish_order
            )
            rows.append(row)
        return rows

    @classmethod
    def create_row(cls, cc_order, wish_order):
        """Return a row for the .csv."""
        row = {key: "" for key in WishBulkfulfilFile.HEADER}
        if cc_order.shipping_rule is not None:
            provider_name = cc_order.shipping_rule.courier_service.courier.name
            provider_name = cls.SHIPPING_PROVIDER_NAME_OVERRIDES.get(
                provider_name, provider_name
            )
            row[cls.SHIPPING_PROVIDER] = provider_name

        else:
            row[cls.SHIPPING_PROVIDER] = cls.DEFAULT_SHIPPING_PROVIDER
        row[cls.ORIGIN_COUNTRY_CODE] = cls.DEFAULT_ORIGIN_CODE
        row[cls.ORDER_ID] = wish_order.wish_order_id
        row[cls.TRACKING_NUMBER] = cc_order.tracking_number
        return [row[key] for key in cls.HEADER]

    @classmethod
    def generate_file(cls, orders):
        """Create a Wish Order Fulfilment file."""
        rows = cls.create_rows(orders)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(cls.HEADER)
        for row in rows:
            writer.writerow(row)
        return output.getvalue()
