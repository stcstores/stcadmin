"""Models for managing the Shopify channel."""

import json
import time
import traceback

import shopify_api_py
from ccapi import CCAPI
from django.db import models
from solo.models import SingletonModel

from inventory.models import ProductExport
from orders.models import Order as CloudCommerceOrder

from .cloud_commerce_order import CreatedOrder, CreateOrder


class ShopifyConfig(SingletonModel):
    """Model for managing configuration for the Shopify channel."""

    channel_id = models.CharField(max_length=20)


class ShopifyImport(models.Model):
    """Model for Shopify order imports."""

    created_at = models.DateTimeField(auto_now_add=True)


class ShopifyOrder(models.Model):
    """Model for imported Shopify orders."""

    shopify_import = models.ForeignKey(ShopifyImport, on_delete=models.CASCADE)
    shopify_order_id = models.CharField(max_length=255)
    order = models.ForeignKey(
        CreatedOrder, blank=True, null=True, on_delete=models.PROTECT
    )
    error = models.TextField(blank=True)
    fulfilled = models.BooleanField(default=False)


class ShopifyFulfillmentError(models.Model):
    """Model for recording errors fulfilling Shopify orders."""

    shopify_order = models.ForeignKey(ShopifyOrder, on_delete=models.CASCADE)
    error = models.TextField(blank=True)


class ShopifyInventoryUpdater:
    """Methods for updating Shopify inventory information."""

    REQUEST_PAUSE = 0.51

    @classmethod
    def update_stock(cls):
        """Update Shopify product stock level and status."""
        stock_levels = cls._get_stock_levels()
        location_id = cls._get_location_id()
        products = cls._get_products()
        cls._update_stock_levels(
            products=products, location_id=location_id, stock_levels=stock_levels
        )

    @classmethod
    @shopify_api_py.shopify_api_session
    def _get_products(cls):
        """Return all Shopify products."""
        return shopify_api_py.products.get_all_products()

    @classmethod
    @shopify_api_py.shopify_api_session
    def _get_location_id(cls):
        """Return all Shopify products."""
        locations = shopify_api_py.locations.get_inventory_locations()
        return locations[0].id

    @classmethod
    def _get_stock_levels(cls):
        inventory_information = ProductExport.objects.latest("timestamp").as_table()
        stock_levels = {
            row["VAR_SKU"]: int(row["VAR_Stock"]) for row in inventory_information
        }
        return stock_levels

    @classmethod
    @shopify_api_py.shopify_api_session
    def _update_stock_levels(cls, products, location_id, stock_levels):
        for product in products:
            for variant in product.variants:
                cls._update_variant_stock(
                    variant=variant, location_id=location_id, stock_levels=stock_levels
                )
            cls._update_product_status(product)

    @classmethod
    def _update_variant_stock(cls, variant, location_id, stock_levels):
        new_stock_level = stock_levels[variant.sku]
        current_stock_level = variant.inventory_quantity
        if current_stock_level != new_stock_level:
            shopify_api_py.products.update_variant_stock(
                variant=variant,
                new_stock_level=new_stock_level,
                location_id=location_id,
            )
            time.sleep(cls.REQUEST_PAUSE)

    @classmethod
    def _update_product_status(cls, product):
        total_stock = sum([variant.inventory_quantity for variant in product.variants])
        if total_stock == 0 and product.status == "active":
            cls._set_product_status(product, "draft")
        elif total_stock > 0 and product.status == "draft":
            cls._set_product_status(product, "active")

    @classmethod
    def _set_product_status(cls, product, status):
        product.status = status
        product.save()
        time.sleep(cls.REQUEST_PAUSE)


class ShopifyOrderImporter:
    """Import new Shopify orders into Cloud Commerce."""

    SHIPPING_ADDRESS_NAME = "name"
    SHIPPING_ADDRESS_COMPANY = "company"
    SHIPPING_ADRESS_LINE_ONE = "address1"
    SHIPPING_ADDRESS_LINE_TWO = "address2"
    SHIPPING_ADDRESS_CITY = "city"
    SHIPPING_ADDRESS_PROVINCE = "province"
    SHIPPING_ADDRESS_ZIP = "zip"
    SHIPPING_ADDRESS_COUNTRY = "country"
    SHIPPING_ADDRESS_COUNTRY_CODE = "country_code"
    SHIPPING_ADDRESS_PHONE = "phone"

    @classmethod
    def import_orders(cls):
        """Import new Shopify orders into Cloud Commerce."""
        import_object = ShopifyImport()
        import_object.save()
        channel_id = ShopifyConfig.get_solo().channel_id
        orders = cls._get_orders()
        for order in orders:
            if ShopifyOrder.objects.filter(
                shopify_order_id=str(order.id), order__isnull=False
            ).exists():
                continue
            try:
                data = cls._get_order_data(order, channel_id)
                created_order = CreateOrder(data).create()
            except Exception as e:
                ShopifyOrder(
                    shopify_import=import_object,
                    shopify_order_id=str(order.id),
                    error=str(e) + traceback.format_exc(),
                ).save()
            else:
                ShopifyOrder(
                    shopify_import=import_object,
                    shopify_order_id=str(order.id),
                    order=created_order,
                ).save()

    @classmethod
    @shopify_api_py.shopify_api_session
    def _get_orders(cls):
        orders = shopify_api_py.orders.get_all_orders()
        orders = [
            order
            for order in orders
            if order.financial_status == "paid"
            and order.confirmed is True
            and order.cancelled_at is None
        ]
        return orders

    @classmethod
    def _get_cc_product_id(cls, sku, channel_id):
        search_results = CCAPI.search_product_SKU(
            sku,
            channel_id=channel_id,
        )
        return search_results[0].variation_id

    @classmethod
    def _get_product_data(cls, order, channel_id):
        products = []
        for line_item in order.line_items:
            product_id = cls._get_cc_product_id(
                sku=line_item.sku, channel_id=channel_id
            )
            product = {
                "product_id": product_id,
                "price": float(line_item.price),
                "quantity": line_item.quantity,
            }
            products.append(product)
        return products

    @classmethod
    def _get_order_data(cls, order, channel_id):
        products = cls._get_product_data(order, channel_id)
        address_details = order.shipping_address.attributes
        data = {
            "basket": json.dumps(products),
            "customer_name": address_details[cls.SHIPPING_ADDRESS_NAME],
            "address_line_1": address_details[cls.SHIPPING_ADRESS_LINE_ONE],
            "address_line_2": address_details[cls.SHIPPING_ADDRESS_LINE_TWO],
            "town": address_details[cls.SHIPPING_ADDRESS_CITY],
            "post_code": address_details[cls.SHIPPING_ADDRESS_ZIP],
            "region": address_details[cls.SHIPPING_ADDRESS_PROVINCE],
            "country": address_details[cls.SHIPPING_ADDRESS_COUNTRY],
            "channel": channel_id,
            "shipping_price": float(order.total_shipping_price_set.shop_money.amount),
            "phone_number": order.customer.phone,
            "email": order.customer.email,
            "sale_price": None,
        }
        return data


class ShopifyFulfillment:
    """Methods for marking Shopify orders fulfilled."""

    @classmethod
    def fulfill_completed_orders(cls):
        """Fulfill completed Shopify orders."""
        orders = cls._get_fulfilled_orders()
        for order in orders:
            cls._mark_order_fulfilled(order)

    @classmethod
    def _get_fulfilled_orders(cls):
        unfulfilled_shopify_orders = ShopifyOrder.objects.filter(
            fulfilled=False, order__isnull=False
        )
        unfulfilled_shopify_order_ids = unfulfilled_shopify_orders.values_list(
            "order__order_id", flat=True
        )
        dispatched_cc_order_ids = set(
            CloudCommerceOrder.objects.filter(
                order_ID__in=unfulfilled_shopify_order_ids, dispatched_at__isnull=False
            ).values_list("order_ID", flat=True)
        )
        return [
            order
            for order in unfulfilled_shopify_orders
            if order.order.order_id in dispatched_cc_order_ids
        ]

    @classmethod
    @shopify_api_py.shopify_api_session
    def _mark_order_fulfilled_on_shopify(cls, order):
        location_id = shopify_api_py.locations.get_inventory_locations()[0].id
        shopify_api_py.fulfillment.create_fulfill_order(
            order_id=order.shopify_order_id, location_id=location_id
        )

    @classmethod
    def _mark_order_fulfilled(cls, order):
        try:
            cls._mark_order_fulfilled_on_shopify(order)
        except Exception as e:
            ShopifyFulfillmentError(
                shopify_order=order, error=str(e) + traceback.format_exc()
            ).save()
        else:
            order.fulfilled = True
            order.save()
