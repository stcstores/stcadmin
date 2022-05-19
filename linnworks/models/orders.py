"""Models for handling Linnworks orders."""

import datetime as dt
from collections import defaultdict

from django.utils.timezone import make_aware

from inventory.models import BaseProduct
from orders.models import Channel, Order, ProductSale
from shipping.models import ShippingService

from .config import LinnworksConfig
from .linnworks_export_files import BaseExportFile


class ProcessedOrdersExport(BaseExportFile):
    """Model for reading Linnworks processed order exports."""

    ORDER_ID = "Order Id"
    REFERENCE_NUMBER = "Reference number"
    EXTERNAL_REFERENCE = "External reference"
    CHANNEL_REFERENCE = "Channel reference"
    SHIPPING_COUNTRY = "Shipping country"
    SHIPPING_COUNTRY_CODE = "Shipping country code"
    BILLING_TOWN = "Billing town"
    RECEIVED_DATE = "Received date"
    PROCESSED_DATE = "Processed date"
    SHIPPING_COST = "Shipping cost"
    ORDER_TAX = "Order tax"
    ORDER_TOTAL = "Order total"
    CURRENCY = "Currency"
    PAID = "Paid"
    STATUS = "Status"
    SOURCE = "Source"
    SUBSOURCE = "SubSource"
    DISPATCH_BY = "Dispatch By"
    CREATED_DATE = "Created Date"
    SHIPPING_SERVICE_NAME = "Shipping service name"
    SHIPPING_SERVICE_TAG = "Shipping service tag"
    SHIPPING_SERVICE_CODE = "Shipping service code"
    SHIPPING_SERVICE_VENDOR = "Shipping service vendor"
    PACKAGING_GROUP = "Packaging group"
    TRACKING_NUMBER = "Tracking number"
    CHANNEL_BUYER_NAME = "Channel buyer name"
    MARKER = "Marker"
    PAYMENT_METHOD = "Payment method"
    ON_HOLD = "On hold"
    FULFILLMENT_LOCATION = "Fulfillment location"
    SKU = "SKU"
    ITEM_TITLE = "Item title"
    ORIGINAL_TITLE = "Original title"
    CHANNEL_SKU = "Channel SKU"
    ITEM_NUMBER = "Item number"
    QUANTITY = "Quantity"
    UNIT_COST = "Unit cost"
    LINE_DISCOUNT = "Line discount"
    TAX_RATE = "Tax rate"
    LINE_TAX = "Line tax"
    LINE_TOTAL_EXCLUDING_TAX = "Line total excluding tax"
    LINE_TOTAL = "Line total"
    IS_SERVICE = "Is service"
    COMPOSITE_PARENT_SKU = "Composite parent SKU"
    COMPOSITE_PARENT_ORDER_ITEM_NUMBER = "Composite parent order item number"
    ORDER_NOTES = "Order Notes"
    TAX_ID = "Tax Id"

    def __init__(self, *args, **kwargs):
        """Load a Linnworks Processed Orders file."""
        self._orders = None
        super().__init__(*args, **kwargs)

    def get_file_path(self):
        """Return the file path of the processed orders file."""
        config = LinnworksConfig.get_solo()
        return config.processed_orders_import_path

    @property
    def orders(self):
        """Return a dict of {order_id: order_row}."""
        if self._orders is None:
            self._orders = self._load_orders()
        return self._orders

    def _load_orders(self):
        orders = defaultdict(list)
        for row in self.rows:
            orders[row[self.ORDER_ID]].append(row)
        return dict(orders)


class OrderUpdater:
    """Model for updating the orders model from a Linnworks export."""

    def update_orders(self):
        """Update the orders model from a Linnworks export."""
        existing_order_ids = set(Order.objects.values_list("order_id", flat=True))
        processed_orders = ProcessedOrdersExport().orders
        for order_id, order_rows in processed_orders.items():
            if order_id in existing_order_ids:
                continue
            row = order_rows[0]
            order = Order(
                order_id=order_id,
                recieved_at=self.parse_date_time(
                    row[ProcessedOrdersExport.RECEIVED_DATE]
                ),
                dispatched_at=self.parse_date_time(
                    row[ProcessedOrdersExport.PROCESSED_DATE]
                ),
                cancelled=False,
                ignored=False,
                channel=self.get_channel(row),
                external_reference=row[ProcessedOrdersExport.EXTERNAL_REFERENCE],
                shipping_service=self.get_shipping_service(row),
                tracking_number=row[ProcessedOrdersExport.TRACKING_NUMBER],
            )
            order.save()
            for order_row in order_rows:
                sku = order_row[ProcessedOrdersExport.SKU]
                product = BaseProduct.objects.get(sku=sku)
                product_sale = ProductSale(
                    order=order,
                    sku=order_row[ProcessedOrdersExport.SKU],
                    name=order_row[ProcessedOrdersExport.ITEM_TITLE],
                    weight=product.weight,
                    quantity=order_row[ProcessedOrdersExport.QUANTITY],
                    price=int(order_row[ProcessedOrdersExport.LINE_TOTAL] * 100),
                    supplier=product.supplier,
                    purchase_price=int(product.purchase_price * 100),
                    vat=int(order_row[ProcessedOrdersExport.LINE_TAX] * 100),
                )
                product_sale.save()

        @staticmethod
        def parse_date_time(date_time_string):
            date, time = date_time_string.split(" ")
            year, month, day = (int(_) for _ in date.split("-"))
            hour, minute, second = (int(_) for _ in time.split(":"))
            return make_aware(
                dt.datetime(
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    second=second,
                )
            )

        @staticmethod
        def get_channel(order_row):
            source = order_row[ProcessedOrdersExport.SOURCE]
            sub_source = order_row[ProcessedOrdersExport.SUBSOURCE]
            return Channel.objects.get(
                linnworks_channel__source=source,
                linnworks_channel__subsource=sub_source,
            )

        @staticmethod
        def get_shipping_service(order_row):
            service_name = order_row[ProcessedOrdersExport.SHIPPING_SERVICE_NAME]
            return ShippingService.objects.get(name=service_name)
