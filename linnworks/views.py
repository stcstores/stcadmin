"""Views for the Linnworks app."""

import json

import linnapi
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from inventory.models import BaseProduct
from inventory.views import InventoryUserMixin
from linnworks import models
from linnworks.models import StockManager


@csrf_exempt
def get_stock_levels(request):
    """Return the stock level for a product."""
    output = {}
    request_data = json.loads(request.body)
    product_ids = request_data["product_ids"]
    products = BaseProduct.objects.filter(pk__in=product_ids)
    stock_levels = StockManager.get_stock_levels(products)
    output = {}
    try:
        for product in products:
            stock_level_object = stock_levels[product.sku]
            output[product.pk] = {
                "stock_level": stock_level_object.stock_level,
                "available": stock_level_object.available,
                "in_orders": stock_level_object.in_orders,
                "in_order_book": stock_level_object.in_order_book,
            }
    except linnapi.exceptions.InvalidResponseError:
        return HttpResponseNotFound()
    else:
        return JsonResponse(output)


@csrf_exempt
def update_stock_levels(request):
    """Return the stock level for a product."""
    output = {}
    request_data = json.loads(request.body)
    for update_data in request_data["stock_updates"]:
        product_id = update_data["product_id"]
        stock_level = int(update_data["new_stock_level"])
        product = get_object_or_404(BaseProduct, pk=product_id)
        stock_level = StockManager.set_stock_level(
            product=product, user=request.user, new_stock_level=stock_level
        )
        output[product.pk] = stock_level
    return JsonResponse(output)


@csrf_exempt
def get_initial_stock_levels(request):
    """Return the stock level for a product."""
    output = {}
    request_data = json.loads(request.body)
    for product_id in request_data["product_ids"]:
        product = get_object_or_404(BaseProduct, pk=product_id)
        stock_level = StockManager.get_initial_stock_level(product) or 0
        output[product_id] = stock_level
    return JsonResponse(output)


@csrf_exempt
def update_initial_stock_levels(request):
    """Return the stock level for a product."""
    output = {}
    request_data = json.loads(request.body)
    for update_data in request_data["stock_updates"]:
        product_id = update_data["product_id"]
        stock_level = int(update_data["new_stock_level"])
        product = get_object_or_404(BaseProduct, pk=product_id)
        stock_level = StockManager.set_initial_stock_level(
            product=product, user=request.user, new_stock_level=stock_level
        )
        output[product.pk] = stock_level
    return JsonResponse(output)


@csrf_exempt
def get_stock_records(request):
    """Return a display of a products stock level according to records."""
    template = get_template("linnworks/stock_record.html")
    request_data = json.loads(request.body)
    product_ids = request_data["product_ids"]
    output = {}
    products = BaseProduct.objects.filter(pk__in=product_ids)
    skus = products.values_list("sku", flat=True)
    stock_records = StockManager.recorded_stock_level(*skus)
    for product in products:
        try:
            stock_record = stock_records[product.sku]
        except KeyError:
            output[product.id] = '<i class="fa-duotone fa-exclamation error"></i>'
        else:
            output[product.pk] = template.render({"stock_record": stock_record})
    return JsonResponse(output)


class StockLevelHistory(InventoryUserMixin, TemplateView):
    """Show a history of stock level changes for a product."""

    template_name = "linnworks/stock_level_history.html"

    def get_context_data(self, *args, **kwargs):
        """Show a history of stock level changes for a product."""
        context = super().get_context_data(*args, **kwargs)
        product = get_object_or_404(BaseProduct, pk=self.kwargs["product_pk"])
        context["product"] = product
        context["stock_history"] = StockManager.get_stock_level_history(product.sku)
        return context


class StockValue(InventoryUserMixin, TemplateView):
    """Show current and past stock values."""

    template_name = "linnworks/stock_value.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the view."""
        context = super().get_context_data(*args, **kwargs)
        context["stock_level_exports"] = models.StockLevelExportUpdate.objects.all()
        return context
