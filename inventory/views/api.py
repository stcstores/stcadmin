"""Views for AJAX requests."""

import json

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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
        sku = models.new_product_sku()
        return HttpResponse(sku)


@method_decorator(csrf_exempt, name="dispatch")
class GetNewRangeSKUView(InventoryUserMixin, View):
    """Return new Product Range SKU."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        sku = models.new_range_sku()
        return HttpResponse(sku)


@method_decorator(csrf_exempt, name="dispatch")
class UpdateStockLevelView(InventoryUserMixin, View):
    """Update product stock level."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        product_ID = self.request.POST["product_ID"]
        product = get_object_or_404(models.Product, product_ID=product_ID)
        new_stock_level = int(self.request.POST["new_stock_level"])
        old_stock_level = int(self.request.POST["old_stock_level"])
        updated_stock_level = product.update_stock_level(
            old=old_stock_level, new=new_stock_level
        )
        return HttpResponse(updated_stock_level)


class GetStockLevelView(InventoryUserMixin, View):
    """Get the current stock level for a product."""

    @method_decorator(csrf_exempt)
    def post(self, request):
        """Process HTTP request."""
        product_ID = self.request.POST["product_ID"]
        product = get_object_or_404(models.Product, product_ID=product_ID)
        response_data = {"product_ID": product_ID, "stock_level": product.stock_level()}
        return HttpResponse(json.dumps(response_data))


@method_decorator(csrf_exempt, name="dispatch")
class SetImageOrderView(InventoryUserMixin, View):
    """Change order of images for a product."""

    @transaction.atomic
    def post(self, *args, **kwargs):
        """Process HTTP request."""
        try:
            data = json.loads(self.request.body)
            product = get_object_or_404(models.Product, pk=data["product_pk"])
            image_order = [int(_) for _ in data["image_order"]]
            images = product.images.active()
            print(set(images.values_list("pk", flat=True)))
            print(set(image_order))
            if not set(images.values_list("pk", flat=True)) == set(image_order):
                raise Exception("Did not get expected image IDs.")
            for image in images:
                image.ordering = image_order.index(image.id)
                image.save()
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
            image = get_object_or_404(models.ProductImage, pk=int(data["image_id"]))
            image.active = False
            image.save()
        except Exception:
            return HttpResponse(status=500)
        return HttpResponse("ok")
