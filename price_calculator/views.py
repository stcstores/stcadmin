"""Views for price_calculator."""

import json

from ccapi import CCAPI
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from inventory.views.views import InventoryUserMixin
from price_calculator import models


class GetShippingPriceView(InventoryUserMixin, View):
    """View for AJAX requests for shipping prices."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        """Return shipping prices as JSON or return server error."""
        try:
            shipping_price_details = self.get_shipping_price_details()
            json_data = json.dumps(shipping_price_details)
        except Exception as e:
            return HttpResponse(status=500)
        return HttpResponse(json_data)

    def get_shipping_price_details(self):
        """Return details of shipping price as dict."""
        country_name = self.request.POST["country"]
        package_type_name = self.request.POST["package_type"]
        weight = int(self.request.POST["weight"])
        price = int(self.request.POST["price"])
        country = get_object_or_404(models.DestinationCountry, name=country_name)
        exchange_rate = country.current_rate()
        postage_price = models.ShippingPrice.objects.get_price(
            country_name, package_type_name, weight, price
        )
        vat_rates = list(postage_price.vat_rates.values())
        if country.min_channel_fee is None:
            min_channel_fee = 0
        else:
            min_channel_fee = int(country.min_channel_fee * exchange_rate)
        data = {
            "price": postage_price.calculate(weight),
            "price_name": postage_price.name,
            "vat_rates": vat_rates,
            "exchange_rate": exchange_rate,
            "currency_code": str(country.currency_code),
            "min_channel_fee": min_channel_fee,
        }
        return data


class RangePriceCalculatorView(InventoryUserMixin, TemplateView):
    """View calcualting prices for an existing Product Range."""

    template_name = "price_calculator/range_price_calculator.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        product_range = CCAPI.get_range(self.kwargs.get("range_id"))
        product_range.products = [
            CCAPI.get_product(p.id) for p in product_range.products
        ]
        context_data["product_range"] = product_range
        context_data["countries"] = models.DestinationCountry.objects.all()
        return context_data


class PriceCalculator(InventoryUserMixin, TemplateView):
    """View for using price calcualtor without an existing Product."""

    template_name = "price_calculator/price_calculator.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["countries"] = models.DestinationCountry.objects.all()
        context_data["package_types"] = models.PackageType.objects.all()
        return context_data
