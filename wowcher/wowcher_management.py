"""Manage Wowcher orders."""

import csv
import datetime
import io
import time
from decimal import Decimal
from pathlib import Path

import openpyxl
import pywowcher
from ccapi import CCAPI, NewOrderItem

from stcadmin import settings
from wowcher import models

pywowcher.session.set_credentials(
    live_key=settings.WOWCHER_KEY, live_secret_token=settings.WOWCHER_SECRET_TOKEN
)


class WowcherManager:
    """Provides methods for managing Wowcher orders."""

    @classmethod
    def get_new_orders(cls):
        """Add all new orders to the database and create them in Cloud Commerce."""
        deals = models.WowcherDeal.active.all()
        orders = []
        for deal in deals:
            orders.extend(cls.update_deal_orders(deal))
        for db_order, wowcher_order in orders:
            create_cloud_commerce_order(db_order=db_order, wowcher_order=wowcher_order)
        return orders

    @classmethod
    def update_dispatched_orders(cls):
        """Update all Wowcher orders that have been dispatched in Cloud Commerce."""
        orders = models.WowcherOrder.to_dispatch.all()
        dispatched_orders = []
        for order in orders:
            dispatched = cls.dispatch_order(order)
            if dispatched:
                dispatched_orders.append(order)
        return dispatched_orders

    @classmethod
    def check_stock_levels(cls):
        """Update the Cloud Commerce stock levels for Wowcher items."""
        items = models.WowcherItem.objects.filter(
            deal__inactive=False, deal__ended__isnull=True
        )
        for item in items:
            stock_level = CCAPI.get_product(item.CC_product_ID).stock_level
            stock_level_record, _ = models.WowcherStockLevelCheck.objects.get_or_create(
                item=item, defaults={"stock_level": stock_level}
            )
            stock_level_record.stock_level = stock_level
            stock_level_record.save()
        alerts = models.WowcherStockLevelCheck.stock_alerts.all()
        cls._unhide_stock_alerts(alerts)
        return alerts

    @classmethod
    def _unhide_stock_alerts(cls, alerts):
        """Remove the hide_stock_alerts propery from items with no stock alert."""
        alert_items = alerts.values_list("item", flat=True)
        models.WowcherItem.objects.exclude(id__in=alert_items).update(
            hide_stock_alert=False
        )

    @classmethod
    def update_deal_orders(cls, deal):
        """
        Add new orders for a deal to the database and create them in Cloud Commerce.

        Return list( (db_order, wowcher_order) ) of orders created.
        """
        new_orders = cls.get_new_orders_for_deal(deal)
        db_orders = []
        orders = []
        for wowcher_order in new_orders:
            db_order = cls.add_order_to_database(deal=deal, wowcher_order=wowcher_order)
            db_orders.append(db_order)
            orders.append((db_order, wowcher_order))
        models.WowcherOrder.objects.bulk_create(db_orders)
        return orders

    @classmethod
    def get_cloud_commerce_order(cls, order_ID):
        """Return an existing order from Cloud Commerce."""
        search_results = cls._make_get_order_request(order_ID)
        if len(search_results) == 0:
            raise Exception(f"Cloud Commerce order {order_ID} not found.")
        if len(search_results) > 1:
            raise Exception(f"Multiple orders found for order ID {order_ID}.")
        return search_results[0]

    @staticmethod
    def _make_get_order_request(order_ID, retries=5):
        for i in range(retries):
            try:
                return CCAPI.get_orders_for_dispatch(search_term=str(order_ID))
            except Exception:
                continue
        raise Exception(
            f"Could not retrieve Cloud Commerce order {order_ID} after {retries} tries."
        )

    @classmethod
    def get_orders_for_deal(cls, deal):
        """Return all existing orders for a Wowcher deal."""
        orders = pywowcher.get_orders(deal_id=deal.deal_ID)
        deal_orders = [_ for _ in orders if str(_.deal_id) == deal.deal_ID]
        return deal_orders

    @classmethod
    def get_new_orders_for_deal(cls, deal):
        """Return all orders for a Wowcher deal that do not exist in the database."""
        existing_wowcher_codes = models.WowcherOrder.objects.filter(
            deal=deal
        ).values_list("wowcher_code", flat=True)
        orders = cls.get_orders_for_deal(deal)
        new_orders = [_ for _ in orders if _.wowcher_code not in existing_wowcher_codes]
        return new_orders

    @classmethod
    def get_order_item(cls, wowcher_order):
        """Return the matching WowcherItem object for a Wowcher order."""
        order_SKU = wowcher_order.items[0].sku
        try:
            if "-" in order_SKU:
                wowcher_ID = order_SKU.split("-")[1]
                return models.WowcherItem.objects.get(wowcher_ID=wowcher_ID)
            else:
                return models.WowcherItem.objects.get(CC_product_ID=order_SKU)
        except models.WowcherItem.DoesNotExist:
            raise Exception(
                (
                    f"No wowcher item found matcing the wowcher SKU {order_SKU} "
                    f"for wowcher deal {wowcher_order.wowcher_code}."
                )
            )

    @classmethod
    def add_order_to_database(cls, deal, wowcher_order):
        """Create a WowcherOrder object for a Wowcher order."""
        item = cls.get_order_item(wowcher_order)
        customer_name = (
            f"{wowcher_order.delivery_first_name} {wowcher_order.delivery_last_name}"
        )
        return models.WowcherOrder(
            deal=deal,
            wowcher_code=wowcher_order.wowcher_code,
            customer_name=customer_name,
            item=item,
            quantity=wowcher_order.items[0].quantity,
        )

    @classmethod
    def dispatch_order(cls, order):
        """Check if an order is dispatched in Cloud Commerce and update it's status."""
        cc_order = cls.get_cloud_commerce_order(order.CC_order_ID)
        if not cls.cc_order_is_dispatched(cc_order):
            return False
        order.dispatched = True
        if cc_order.tracking_code:
            order.tracking_code = cc_order.tracking_code
        order.save()
        return True

    @staticmethod
    def cc_order_is_dispatched(cc_order):
        """Return True if cc_order is dispatched, otherwise return False."""
        if cc_order.dispatch_date < datetime.datetime(year=2001, month=1, day=1):
            return False
        else:
            return True


class DeliveryStatusFile:
    """Create a Wowcher delivery status file."""

    @classmethod
    def new(cls):
        """Return the filename and contents of a new delivery status file."""
        orders = models.WowcherOrder.for_delivery_status_file.all()
        return cls._save_to_database(orders)

    @classmethod
    def contents(cls, delivery_status_file):
        """Return the filename and contents of an existing delivery status file."""
        orders = delivery_status_file.wowcherorder_set.all()
        file_contents = cls._create_file(orders)
        return cls._filename(delivery_status_file), file_contents

    @classmethod
    def _rows(cls, orders):
        return [cls._order_row(_) for _ in orders]

    @classmethod
    def _order_row(cls, order):
        """Return a delivery status file row for order."""
        row = [order.wowcher_code, "Dispatched"]
        if order.tracking_code:
            row.extend(["Royal Mail", order.tracking_code])
        return row

    @classmethod
    def _create_file(cls, orders):
        """Return the delivery status file as a CSV string."""
        rows = cls._rows(orders)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)
        return output.getvalue()

    @staticmethod
    def _filename(delivery_status_file):
        """Return the file name for the delivery status file."""
        date = delivery_status_file.time_created.strftime("%Y-%m-%d")
        return f"delivery_status_file_{date}.csv"

    @staticmethod
    def _save_to_database(orders):
        """Add the delivery status file to the database."""
        delivery_status_file = models.WowcherDeliveryStatusFile()
        delivery_status_file.save()
        orders.update(delivery_status_file=delivery_status_file)
        return delivery_status_file


class ProofOfDeliveryFile:
    """Create a Wowcher poof of delivery file."""

    template_path = Path(__file__).parent / "proof_of_delivery_template.xlsx"
    first_row = 3

    WOWHCHER_CODE_COLUMN = "A"
    DEAL_ID_COLUMN = "B"
    CUSTOMER_NAME_COLUMN = "C"
    CUSTOMER_EMAIL_COLUMN = "D"
    POST_CODE_COLUMN = "E"
    COURIER_COLUMN = "G"
    TRACKING_CODE_COLUMN = "H"

    @classmethod
    def new(cls):
        """Return the filename and contents of a new proof of delivery file."""
        orders = models.WowcherOrder.for_proof_of_delivery_file.all()
        return cls._save_to_database(orders)

    @classmethod
    def contents(cls, proof_of_delivery_file):
        """Return the filename and contents of an existing proof of delivery file."""
        orders = proof_of_delivery_file.wowcherorder_set.all()
        wowcher_orders = cls._get_wowcher_orders()
        file_contents = cls._create_file(orders, wowcher_orders)
        return cls._filename(proof_of_delivery_file), file_contents

    @classmethod
    def _create_file(cls, orders, wowcher_orders):
        """Return a proof of delivery file as BytesIO."""
        workbook = openpyxl.load_workbook(filename=cls.template_path)
        worksheet = workbook.active
        row_number = cls.first_row
        for order in orders:
            cls._add_order(worksheet, row_number, order, wowcher_orders)
            row_number += 1
        return io.BytesIO(openpyxl.writer.excel.save_virtual_workbook(workbook))

    @classmethod
    def _add_order(cls, worksheet, row, order, wowcher_orders):
        """Add an order to the proof of delivery file."""
        wowcher_order = cls._get_wowcher_order(order, wowcher_orders)
        cls._write_cell(worksheet, row, cls.WOWHCHER_CODE_COLUMN, order.wowcher_code)
        cls._write_cell(worksheet, row, cls.DEAL_ID_COLUMN, order.deal.deal_ID)
        cls._write_cell(worksheet, row, cls.CUSTOMER_NAME_COLUMN, order.customer_name)
        cls._write_cell(
            worksheet, row, cls.CUSTOMER_EMAIL_COLUMN, wowcher_order.delivery_email
        )
        cls._write_cell(
            worksheet, row, cls.POST_CODE_COLUMN, wowcher_order.delivery_postcode
        )
        cls._write_cell(worksheet, row, cls.COURIER_COLUMN, "ROYAL MAIL")
        cls._write_cell(
            worksheet, row, cls.TRACKING_CODE_COLUMN, order.tracking_code or ""
        )

    @staticmethod
    def _save_to_database(orders):
        """Add the proof of delivery file to the database."""
        proof_of_delivery_file = models.WowcherProofOfDeliveryFile()
        proof_of_delivery_file.save()
        orders.update(proof_of_delivery_file=proof_of_delivery_file)
        return proof_of_delivery_file

    def _filename(self):
        datestring = datetime.datetime.now().strftime("%Y-%m-%d")
        return f"proof_of_delivery_{datestring}.xlsx"

    @classmethod
    def _write_cell(self, worksheet, row, column, value):
        cell = str(column) + str(row)
        worksheet[cell] = value

    @staticmethod
    def _get_wowcher_orders():
        wowcher_orders = {}
        for deal in models.WowcherDeal.active.all():
            wowcher_orders[deal.deal_ID] = WowcherManager.get_orders_for_deal(deal)
        return wowcher_orders

    @staticmethod
    def _get_wowcher_order(order, wowcher_orders):
        deal_orders = wowcher_orders[order.deal.deal_ID]
        for wowcher_order in deal_orders:
            if wowcher_order.wowcher_code == order.wowcher_code:
                return wowcher_order
        raise Exception(f"Could not find Wowcher Order {order.wowcher_code}.")


class create_cloud_commerce_order:
    """Create a Wowcher order in Cloud Commerce."""

    SELLING_CHANNEL_ID = "3541"
    LOGIN_ID = 4419651
    BANK_ACCOUNT_ID = 733

    @classmethod
    def __init__(cls, db_order, wowcher_order):
        """Create a Wowcher order in Cloud Commerce."""
        order_price = Decimal(wowcher_order.price) + db_order.deal.shipping_price
        customer_ID = cls._add_customer(db_order=db_order, wowcher_order=wowcher_order)
        billing_address_ID = cls._add_address(
            customer_ID=customer_ID, address_type="Billing", wowcher_order=wowcher_order
        )
        delivery_address_ID = cls._add_address(
            customer_ID=customer_ID,
            address_type="Delivery",
            wowcher_order=wowcher_order,
        )
        order_items = cls._get_order_items(
            db_order=db_order, wowcher_order=wowcher_order, order_price=order_price
        )
        cloud_commerce_order = cls._create_order(
            wowcher_order=wowcher_order,
            customer_ID=customer_ID,
            delivery_address_ID=delivery_address_ID,
            billing_address_ID=billing_address_ID,
            order_items=order_items,
        )
        time.sleep(0.5)
        cls._create_payment(
            customer_ID=customer_ID,
            order_price=order_price,
            invoice_ID=cloud_commerce_order.invoice_id,
        )
        cls._add_CC_order_to_database(
            order=db_order,
            order_ID=cloud_commerce_order.order_id,
            customer_ID=customer_ID,
        )

    @classmethod
    def _add_customer(cls, db_order, wowcher_order):
        """Add a new customer to Cloud Commerce based on the Wowcher order details."""
        return CCAPI.add_customer(
            customer_name=db_order.customer_name,
            address_1=wowcher_order.delivery_line_1,
            address_2=wowcher_order.delivery_line_2,
            town=wowcher_order.delivery_city,
            country=wowcher_order.delivery_country,
            post_code=wowcher_order.delivery_postcode,
            selling_channel_id=cls.SELLING_CHANNEL_ID,
        )

    @classmethod
    def _add_address(cls, customer_ID, address_type, wowcher_order):
        """Add a customer address to Cloud Commerce based on the Wowcher order details."""
        return CCAPI.add_address(
            customer_ID,
            first_name=wowcher_order.delivery_first_name,
            last_name=wowcher_order.delivery_last_name,
            address_type=address_type,
            address_1=wowcher_order.delivery_line_1,
            address_2=wowcher_order.delivery_line_2,
            town=wowcher_order.delivery_city,
            country="United Kingdom",
            post_code=wowcher_order.delivery_postcode,
        )

    @classmethod
    def _get_order_items(cls, db_order, wowcher_order, order_price):
        """Return a list of ccapi.NewOrderItem for each item in a Wowcher order."""
        item_price = cls._item_price_estimate(wowcher_order)
        return [
            cls._get_order_item(
                db_order=db_order,
                wowcher_order=wowcher_order,
                item=item,
                item_price=item_price,
                order_price=order_price,
            )
            for item in wowcher_order.items
        ]

    @classmethod
    def _item_price_estimate(cls, wowcher_order):
        """Return the estimated price per item of wowcher_order."""
        return round(
            Decimal(wowcher_order.price)
            / sum((item.quantity for item in wowcher_order.items)),
            2,
        )

    @classmethod
    def _get_order_item(cls, db_order, wowcher_order, item, item_price, order_price):
        """Return a ccapi.NewOrderItem for the Wowcher order."""
        new_order = NewOrderItem(
            product_id=db_order.item.CC_product_ID,
            item_net=item_price,
            item_gross=item_price + db_order.deal.shipping_price,
            total_net=item_price * item.quantity,
            total_gross=order_price,
            item_discount_net=0,
            quantity=item.quantity,
        )
        return new_order

    @classmethod
    def _create_order(
        cls,
        wowcher_order,
        customer_ID,
        delivery_address_ID,
        billing_address_ID,
        order_items,
    ):
        """Create the order in Cloud Commerce."""
        return CCAPI.create_order(
            items=order_items,
            customer_id=str(customer_ID),
            delivery_address_id=str(delivery_address_ID),
            billing_address_id=str(billing_address_ID),
            delivery_date=datetime.datetime.now() + datetime.timedelta(days=5),
            carriage_net=0,
            carriage_vat=0,
            total_net=float(wowcher_order.price),
            total_vat=round(float(wowcher_order.price) * 0.2, 2),
            total_gross=float(wowcher_order.price),
            discount_net=0,
        )

    @classmethod
    def _create_payment(cls, customer_ID, order_price, invoice_ID):
        """Mark the Cloud Commerce order as paid."""
        CCAPI.insert_payment(
            customer_ID=customer_ID,
            login_ID=cls.LOGIN_ID,
            amount=order_price,
            bank_account_ID=cls.BANK_ACCOUNT_ID,
            invoice_ID=invoice_ID,
            channel_ID=cls.SELLING_CHANNEL_ID,
        )

    @classmethod
    def _add_CC_order_to_database(cls, order, order_ID, customer_ID):
        """Add the Cloud Commerce order ID and customer ID to the order."""
        order.CC_order_ID = order_ID
        order.CC_customer_ID = customer_ID
        order.save()
