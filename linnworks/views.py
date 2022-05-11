"""Views for the Linnworks app."""

import json

import linnapi
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from inventory.models import BaseProduct
from linnworks.models import StockManager


@csrf_exempt
def get_stock_levels(request):
    """Return the stock level for a product."""
    output = {}
    request_data = json.loads(request.body)
    try:
        for product_id in request_data["product_ids"]:
            product = get_object_or_404(BaseProduct, pk=product_id)
            stock_level = StockManager.get_stock_level(product)
            output[product_id] = stock_level
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
    try:
        for product_id in request_data["product_ids"]:
            product = get_object_or_404(BaseProduct, pk=product_id)
            stock_level = StockManager.get_initial_stock_level(product)
            output[product_id] = stock_level
    except linnapi.exceptions.InvalidResponseError:
        return HttpResponseNotFound()
    else:
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
