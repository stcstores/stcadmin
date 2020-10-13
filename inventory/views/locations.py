"""View for updating Product Warehouse Bays."""

import json
import time

from ccapi import CCAPI
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.base import TemplateView

from inventory import models

from .views import InventoryUserMixin


class LocationFormView(InventoryUserMixin, TemplateView):
    """View for LocationsFormSet."""

    template_name = "inventory/locations.html"

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        product_range = CCAPI.get_range(self.kwargs.get("range_id"))
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = product_range
        context["products"] = [
            self.get_product_dict(product) for product in product_range.products
        ]
        context["bays"] = list(models.Bay.objects.values_list("name", flat=True))
        return context

    def get_product_dict(self, product):
        """Return a dict of product details."""
        bay_ids = [bay.id for bay in CCAPI.get_bays_for_product(product.id)]
        bays = models.Bay.objects.filter(bay_ID__in=bay_ids).values("bay_ID", "name")
        return {
            "id": product.id,
            "stock_level": product.stock_level,
            "name": product.full_name,
            "bays": bays,
        }


@method_decorator(csrf_exempt, name="dispatch")
class UpdateProductBays(View):
    """Update the bays in which a product is stored."""

    def post(self, *args, **kwargs):
        """Update the bays in which a product is stored."""
        received_json_data = json.loads(self.request.body.decode("utf-8"))
        response = {}
        for product in received_json_data:
            updated = False
            product_id = product["product_id"]
            add = product.get("add", [])
            remove = product.get("remove", [])
            new_bays = product.get("original")
            add_ids = models.Bay.objects.filter(name__in=add).values_list(
                "bay_ID", flat=True
            )
            remove_ids = models.Bay.objects.filter(name__in=remove).values_list(
                "bay_ID", flat=True
            )
            for bay_id in remove_ids:
                CCAPI.remove_warehouse_bay_from_product(product_id, bay_id)
                updated = True
            for bay_id in add_ids:
                CCAPI.add_warehouse_bay_to_product(product_id, bay_id)
                updated = True
            if updated:
                time.sleep(1)
                new_bays = [bay.name for bay in CCAPI.get_bays_for_product(product_id)]
            response[product_id] = {"bays": new_bays}
        return JsonResponse(response)
