"""Views for AJAX requests."""

import json

from ccapi import CCAPI
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
            product = get_object_or_404(models.Product, product_ID=data["product_ID"])
            image_order = data["image_order"]
            images = models.ProductImage.objects.filter(product=product)
            if not set(images.values_list("image_ID", flat=True)) == set(image_order):
                raise Exception("Did not get expected image IDs.")
            for image in images:
                image.position = image_order.index(image.image_ID)
                image.save()
            models.ProductImage.update_CC_image_order(product)
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
            image = get_object_or_404(models.ProductImage, image_ID=data["image_id"])
            CCAPI.delete_image(image.image_ID)
            image.delete()
        except Exception:
            return HttpResponse(status=500)
        return HttpResponse("ok")
