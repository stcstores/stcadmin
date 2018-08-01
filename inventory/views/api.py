"""Views for AJAX requests."""

import json

from ccapi import CCAPI
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .views import InventoryUserMixin


class GetNewSKUView(InventoryUserMixin, View):
    """Return new Product SKU."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        """Process HTTP request."""
        sku = CCAPI.get_sku(range_sku=False)
        return HttpResponse(sku)


class GetNewRangeSKUView(InventoryUserMixin, View):
    """Return new Product Range SKU."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        """Process HTTP request."""
        sku = CCAPI.get_sku(range_sku=True)
        return HttpResponse(sku)


class GetStockForProductView(InventoryUserMixin, View):
    """Return stock number for product."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
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


class UpdateStockLevelView(InventoryUserMixin, View):
    """Update product stock level."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        """Process HTTP request."""
        request_data = json.loads(self.request.body)
        product_id = request_data["product_id"]
        new_stock_level = request_data["new_stock_level"]
        old_stock_level = request_data["old_stock_level"]
        CCAPI.update_product_stock_level(
            product_id=product_id,
            new_stock_level=new_stock_level,
            old_stock_level=old_stock_level,
        )
        product = CCAPI.get_product(product_id)
        stock_level = product.stock_level
        return HttpResponse(stock_level)


class SetImageOrderView(InventoryUserMixin, View):
    """Change order of images for a product."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        """Process HTTP request."""
        try:
            data = json.loads(self.request.body)
            CCAPI.set_image_order(
                product_id=data["product_id"], image_ids=data["image_order"]
            )
        except Exception:
            return HttpResponse(status=500)
        return HttpResponse("ok")


class DeleteImage(InventoryUserMixin, View):
    """Remove image from a product."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        """Process HTTP request."""
        try:
            data = json.loads(self.request.body)
            CCAPI.delete_image(data["image_id"])
        except Exception:
            return HttpResponse(status=500)
        return HttpResponse("ok")
