"""Views for the epos app."""

import json

from ccapi import CCAPI
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from home.views import UserInGroupMixin


class EPOSUserMixin(UserInGroupMixin):
    """View mixin to ensure that user in in the epos group."""

    groups = ["epos"]


class Index(EPOSUserMixin, TemplateView):
    """View for the epos page."""

    template_name = "epos/index.html"


class BarcodeSearch(EPOSUserMixin, View):
    """AJAX request view to return product data by barcode."""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Mark view as CSRF exempt."""
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Search for products matching barcode and return relevent data."""
        barcode = request.POST["barcode"]
        search_result = CCAPI.search_products(barcode)
        if len(search_result) == 0:
            return HttpResponse("Not Found")
        product = search_result[0]
        product_id = str(search_result[0].variation_id)
        product = CCAPI.get_product(product_id)
        data = {
            "id": product.id,
            "name": product.full_name,
            "sku": product.sku,
            "barcode": product.barcode,
            "base_price": float(product.base_price),
            "vat_rate": product.vat_rate,
            "stock_level": product.stock_level,
            "order_quantity": 1,
        }
        return HttpResponse(json.dumps(data))


class EPOSOrder(EPOSUserMixin, View):
    """AJAX request view to update stock levels according to an EPOS order."""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Mark view as CSRF exempt."""
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Update Cloud Commerce stock levels."""
        products = json.loads(request.body)
        for product_id, product in products.items():
            old_stock_level = product["stock_level"]
            new_stock_level = int(product["stock_level"]) - int(
                product["order_quantity"]
            )
            CCAPI.update_product_stock_level(
                product_id=product_id,
                new_stock_level=new_stock_level,
                old_stock_level=old_stock_level,
            )
        return HttpResponse("ok")
