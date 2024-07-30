"""Views for the UPS Manifestor application."""

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from inventory.models import BaseProduct

from .fba import FBAUserMixin


class PurchasePriceBySku(FBAUserMixin, View):
    """Return a product's purchase price by SKU."""

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        """Make CSRF exempt."""
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Return a product's purchase price by SKU."""
        try:
            sku = self.request.POST["sku"]
            product = get_object_or_404(BaseProduct, sku=sku)
            return JsonResponse({"purchase_price": product.purchase_price})
        except Exception:
            return HttpResponseBadRequest()
