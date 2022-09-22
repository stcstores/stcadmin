"""Models for handling Linnworks orders."""

import datetime as dt
import logging
import time
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import linnapi
from django.db import models, transaction
from django.utils import timezone

from home.models import Staff
from inventory.models import BaseProduct
from orders.models import Order, ProductSale
from shipping.models import Country, Currency, ShippingService

from .config import LinnworksChannel, LinnworksConfig
from .linnworks_export_files import BaseExportFile

logger = logging.getLogger("management_commands")


class LinnworksOrderManager(models.Manager):
    """Model manager for the LinnworksOrder model."""

    def get_recent_orders(self, orders_since=None):
        """Return orders dispatched after a datetime."""
        if orders_since is None:
            orders_since = timezone.now() - dt.timedelta(days=30)
        return Order.objects.filter(dispatched_at__gte=orders_since)

    def update_order_guids(self, orders_since=None):
        """Add Linnworks order GUIDs to recent orders."""
        orders = self.get_recent_orders(orders_since).filter(
            linnworks_order__isnull=True
        )
        wait_time = 60
        for i, order in enumerate(orders):
            try:
                guid = get_order_guid(order.order_id)
                LinnworksOrder(order=order, order_guid=guid).save()
            except Exception as e:
                logger.exception(e)
                continue
            if i > 0 and i % 149 == 0:
                time.sleep(wait_time)

    def update_packing_records(self, orders_since=None):
        """Add Linnworks order GUIDs to recent orders."""
        staff = {
            _.email_address: _
            for _ in Staff.objects.filter(email_address__isnull=False)
        }
        orders = (
            self.get_recent_orders(orders_since)
            .filter(linnworks_order__order_guid__isnull=False, packed_by__isnull=True)
            .select_related("linnworks_order")
        )
        wait_time = 60
        for i, order in enumerate(orders):
            try:
                audits = get_order_audit_trail(order.linnworks_order.order_guid)
                for audit in audits:
                    if audit.audit_type == "ORDER_PROCESSED":
                        order.packed_by = staff[audit.updated_by]
                        order.save()
                        break
            except Exception as e:
                logger.exception(e)
                continue
            finally:
                if i > 0 and i % 149 == 0:
                    time.sleep(wait_time)


class LinnworksOrder(models.Model):
    """Model for storing order properties related to Linnworks."""

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="linnworks_order"
    )
    order_guid = models.CharField(max_length=36)

    objects = LinnworksOrderManager()

    class Meta:
        """Meta class for the linnworks.LinnworksOrder model."""

        verbose_name = "Linnworks Order"
        verbose_name_plural = "Linnworks Orders"


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
        """Return the path to the latest inventory export."""
        config = LinnworksConfig.get_solo()
        order_export_file_dir = config.processed_orders_import_path
        exports = sorted(list(Path(order_export_file_dir).iterdir()))
        return exports[-1]

    @property
    def orders(self):
        """Return a dict of {order_id: order_row}."""
        if self._orders is None:
            self._orders = self._load_orders()
        return self._orders

    def _load_orders(self):
        orders = defaultdict(list)
        for row in self.rows:
            if row[self.REFERENCE_NUMBER] == "MERGED":
                continue
            orders[row[self.ORDER_ID]].append(row)
        return dict(orders)


class OrderUpdater:
    """Model for updating the orders model from a Linnworks export."""

    def __init__(self):
        """Retrieve reusable values from the database."""
        self.currencies = {
            currency.code: currency for currency in Currency.objects.all()
        }
        self.channels = {
            channel.sub_source: channel.channel
            for channel in LinnworksChannel.objects.all()
        }
        self.countries = {
            country.ISO_code: country for country in Country.objects.all()
        }
        self.shipping_services = {
            service.full_name: service for service in ShippingService.objects.all()
        }

    @transaction.atomic()
    def update_orders(self, processed_orders_export=None):
        """Update the orders model from a Linnworks export."""
        existing_order_ids = set(Order.objects.values_list("order_id", flat=True))
        processed_orders_export = processed_orders_export or ProcessedOrdersExport()
        processed_orders = processed_orders_export.orders
        for order_id, order_rows in processed_orders.items():
            if order_id in existing_order_ids:
                continue
            row = order_rows[0]
            order = self.create_order(order_id, row)
            order.save()
            order_skus = []
            for product_row in order_rows:
                if product_row[ProcessedOrdersExport.COMPOSITE_PARENT_SKU]:
                    continue
                if product_row[ProcessedOrdersExport.SKU] in order_skus:
                    product_sale = ProductSale.objects.get(
                        sku=product_row[ProcessedOrdersExport.SKU],
                        order__order_id=order_id,
                    )
                    product_sale.quantity += int(
                        product_row[ProcessedOrdersExport.QUANTITY]
                    )
                    product_sale.save()
                else:
                    product_sale = self.create_product_sale(order, product_row)
                    product_sale.save()
                    order_skus.append(product_sale.sku)
            try:
                order._set_calculated_shipping_price()
            except Exception:
                pass

    def create_order(self, order_id, row):
        """Return an orders.Order instance."""
        cols = ProcessedOrdersExport
        currency = self.currencies[row[cols.CURRENCY]]
        shipping_service = self.get_shipping_service(row)
        order = Order(
            order_id=order_id,
            recieved_at=self.parse_date_time(row[cols.RECEIVED_DATE]),
            dispatched_at=self.parse_date_time(row[cols.PROCESSED_DATE]),
            channel=self.get_channel(row[cols.SOURCE], row[cols.SUBSOURCE]),
            external_reference=row[cols.EXTERNAL_REFERENCE],
            country=self.countries[row[cols.SHIPPING_COUNTRY_CODE]],
            shipping_service=shipping_service,
            tracking_number=row[cols.TRACKING_NUMBER],
            priority=shipping_service.priority if shipping_service else False,
            displayed_shipping_price=self.convert_integer_price(
                row[cols.SHIPPING_COST]
            ),
            tax=self.convert_integer_price(row[cols.ORDER_TAX]),
            currency=currency,
            total_paid=self.convert_integer_price(row[cols.ORDER_TOTAL]),
            total_paid_GBP=self.convert_integer_price(
                Decimal(row[cols.ORDER_TOTAL]) * currency.exchange_rate
            ),
        )
        return order

    def create_product_sale(self, order, product_row):
        """Return an orders.ProductSale instance."""
        cols = ProcessedOrdersExport
        sku = product_row[cols.SKU]
        product = BaseProduct.objects.get(sku=sku)
        product_sale = ProductSale(
            order=order,
            sku=product_row[cols.SKU],
            name=product_row[cols.ITEM_TITLE],
            weight=product.weight_grams,
            quantity=product_row[cols.QUANTITY],
            supplier=product.supplier,
            purchase_price=self.convert_integer_price(product.purchase_price),
            tax=self.convert_integer_price(product_row[cols.LINE_TAX]),
            unit_price=self.convert_integer_price(product_row[cols.UNIT_COST]),
            item_price=self.convert_integer_price(product_row[cols.LINE_TOTAL]),
            item_total_before_tax=self.convert_integer_price(
                product_row[cols.LINE_TOTAL_EXCLUDING_TAX]
            ),
        )
        return product_sale

    @staticmethod
    def convert_integer_price(decimal_price):
        """Return a price in pence."""
        return int(float(decimal_price) * 100)

    @staticmethod
    def parse_date_time(date_time_string):
        """Return a date time string as datetime.datetime."""
        date, time = date_time_string.split(" ")
        year, month, day = (int(_) for _ in date.split("-"))
        hour, minute, second = (int(_) for _ in time.split(":"))
        return timezone.make_aware(
            dt.datetime(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                second=second,
            )
        )

    def get_channel(self, source, subsource):
        """Return the channel an order was recieved from."""
        if source == "DIRECT":
            return None
        return self.channels[subsource]

    def get_shipping_service(self, order_row):
        """Return a shipping.Shiping service instance."""
        service_name = order_row[ProcessedOrdersExport.SHIPPING_SERVICE_NAME]
        if service_name == "Default":
            return None
        return self.shipping_services[service_name]


@linnapi.linnworks_api_session
def get_order_guid(order_id):
    """Return the Linnworks order GUID for an order."""
    return linnapi.orders.get_order_guid_by_order_id(order_id)


@linnapi.linnworks_api_session
def get_order_audit_trail(order_guid):
    """Return the audit trail for an order."""
    return linnapi.orders.get_processed_order_audit_trail(order_guid)
