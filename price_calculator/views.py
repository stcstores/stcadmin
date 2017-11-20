import json

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from inventory.views.views import InventoryUserMixin
from price_calculator import models
from ccapi import CCAPI
from django.views.generic.base import TemplateView


class GetShippingPriceView(InventoryUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        try:
            country_name = request.POST['country']
            package_type_name = request.POST['package_type']
            weight = int(request.POST['weight'])
            price = int(request.POST['price'])
            postage_price = models.ShippingPrice.objects.get_price(
                country_name, package_type_name, weight, price)
            vat_rates = list(postage_price.vat_rates.values())
            return HttpResponse(json.dumps({
                'price': postage_price.calculate(weight),
                'price_name': postage_price.name,
                'vat_rates': vat_rates,
            }))
        except Exception as e:
            return HttpResponse(status=500)


class RangePriceCalculatorView(InventoryUserMixin, TemplateView):
    template_name = 'price_calculator/range_price_calculator.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        product_range = CCAPI.get_range(
            self.kwargs.get('range_id'))
        product_range.products = [
            CCAPI.get_product(p.id) for p in product_range.products]
        context_data['product_range'] = product_range
        context_data['countries'] = models.DestinationCountry.objects.all()
        return context_data


class PriceCalculator(InventoryUserMixin, TemplateView):
    template_name = 'price_calculator/price_calculator.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['countries'] = models.DestinationCountry.objects.all()
        context_data['package_types'] = models.PackageType.objects.all()
        return context_data
