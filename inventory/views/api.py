import json

from ccapi import CCAPI
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .views import InventoryUserMixin
from django.views import View


class GetNewSKU(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        sku = CCAPI.get_sku(range_sku=False)
        return HttpResponse(sku)


class GetNewRangeSKU(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        sku = CCAPI.get_sku(range_sku=True)
        return HttpResponse(sku)


class GetStockForProduct(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        variation_ids = json.loads(self.request.body)['variation_ids']
        stock_data = []
        for variation_id in variation_ids:
            product = CCAPI.get_product(variation_id)
            stock_data.append({
                'variation_id': variation_id,
                'stock_level': product.stock_level,
                'locations': ' '.join(
                    [location.name for location in product.locations])})
        return HttpResponse(json.dumps(stock_data))


class UpdateStockLevel(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        request_data = json.loads(self.request.body)
        product_id = request_data['product_id']
        new_stock_level = request_data['new_stock_level']
        old_stock_level = request_data['old_stock_level']
        CCAPI.update_product_stock_level(
            product_id, new_stock_level, old_stock_level)
        product = CCAPI.get_product(product_id)
        stock_level = product.stock_level
        return HttpResponse(stock_level)
