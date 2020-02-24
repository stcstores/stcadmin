"""Views for AJAX requests."""

import json

from ccapi import CCAPI
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from inventory import models

from .views import InventoryUserMixin


@method_decorator(csrf_exempt, name="dispatch")
class GetNewSKUView(InventoryUserMixin, View):
    """Return new Product SKU."""

    def post(*args, **kwargs):
        """Return a new product SKU."""
        sku = CCAPI.get_sku(range_sku=False)
        return HttpResponse(sku)


@method_decorator(csrf_exempt, name="dispatch")
class GetNewRangeSKUView(InventoryUserMixin, View):
    """Return new Product Range SKU."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        sku = CCAPI.get_sku(range_sku=True)
        return HttpResponse(sku)


@method_decorator(csrf_exempt, name="dispatch")
class GetStockForProductView(InventoryUserMixin, View):
    """Return stock number for product."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        variation_ids = json.loads(self.request.body)["variation_ids"]
        stock_data = []
        for variation_id in variation_ids:
            product = CCAPI.get_product(variation_id)
            stock_data.append(
                {
                    "variation_id": variation_id,
                    "stock_level": product.stock_level,
                    "locations": " ".join(
                        [location.name for location in product.locations]
                    ),
                }
            )
        return HttpResponse(json.dumps(stock_data))


@method_decorator(csrf_exempt, name="dispatch")
class UpdateStockLevelView(InventoryUserMixin, View):
    """Update product stock level."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        request_data = json.loads(self.request.body)
        product_id = request_data["product_id"]
        product_sku = request_data["sku"]
        new_stock_level = request_data["new_stock_level"]
        old_stock_level = request_data["old_stock_level"]
        models.StockChange(
            product_id=product_id,
            product_sku=product_sku,
            stock_before=new_stock_level,
            stock_after=old_stock_level,
            user=self.request.user,
        ).save()
        CCAPI.update_product_stock_level(
            product_id=product_id,
            new_stock_level=new_stock_level,
            old_stock_level=old_stock_level,
        )
        product = CCAPI.get_product(product_id)
        stock_level = product.stock_level
        return HttpResponse(stock_level)


@method_decorator(csrf_exempt, name="dispatch")
class SetImageOrderView(InventoryUserMixin, View):
    """Change order of images for a product."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        try:
            data = json.loads(self.request.body)
            CCAPI.set_image_order(
                product_id=data["product_id"], image_ids=data["image_order"]
            )
        except Exception:
            return HttpResponse(status=500)
        return HttpResponse("ok")


@method_decorator(csrf_exempt, name="dispatch")
class DeleteImage(InventoryUserMixin, View):
    """Remove image from a product."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        try:
            data = json.loads(self.request.body)
            CCAPI.delete_image(data["image_id"])
        except Exception:
            return HttpResponse(status=500)
        return HttpResponse("ok")
