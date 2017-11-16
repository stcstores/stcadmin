import json

from ccapi import CCAPI
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from inventory import models

from .views import InventoryUserMixin


class GetNewSKUView(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        sku = CCAPI.get_sku(range_sku=False)
        return HttpResponse(sku)


class GetNewRangeSKUView(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        sku = CCAPI.get_sku(range_sku=True)
        return HttpResponse(sku)


class GetStockForProductView(InventoryUserMixin, View):

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


class UpdateStockLevelView(InventoryUserMixin, View):

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


class SetImageOrderView(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        try:
            data = json.loads(self.request.body)
            response = CCAPI.set_image_order(
                product_id=data['product_id'], image_ids=data['image_order'])
            response.raise_for_status()
        except Exception:
            return HttpResponse(status=500)
        return HttpResponse('ok')


class DeleteImage(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        try:
            data = json.loads(self.request.body)
            CCAPI.delete_image(data['image_id'])
        except Exception:
            return HttpResponse(status=500)
        return HttpResponse('ok')


class GetShippingPriceView(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        try:
            country_name = request.POST['country']
            package_type_name = request.POST['package_type']
            weight = int(request.POST['weight'])
            price_obj = models.ShippingPrice.objects.get_price(
                country_name, package_type_name, weight)
            price = price_obj.calculate(weight)
            return HttpResponse(json.dumps({
                'price': price,
                'price_name': price_obj.name,
            }))
        except Exception as e:
            raise e
            return HttpResponse(status=500)
