"""Views for price_calculator."""

import json

import cc_products
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

    SUCCESS = "success"
    PRICE = "price"
    PRICE_NAME = "price_name"
    VAT_RATES = "vat_rates"
    EXCHANGE_RATE = "exchange_rate"
    CURRENCY_CODE = "currency_code"
    CURRENCY_SYMBOL = "currency_symbol"
    MIN_CHANNEL_FEE = "min_channel_fee"

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        """Return shipping prices as JSON or return server error."""
        try:
            json_data = self.get_shipping_price_details()
        except Exception:
            json_data = self.no_shipping_price_response()
        return HttpResponse(json_data)

    def package_type_name(self):
        """Return the package type name."""
        int_shipping = self.request.POST["international_shipping"]
        if (
            self.country.shipping_region.name != "Domestic"
            and int_shipping == "Express"
        ):
            package_type_name = int_shipping
        else:
            package_type_name = self.request.POST["package_type"]
        return package_type_name

    def min_channel_fee(self):
        """Return the minimum channel fee."""
        if self.country.min_channel_fee is None:
            min_channel_fee = 0
        else:
            min_channel_fee = int(self.country.min_channel_fee * self.exchange_rate)
        return min_channel_fee

    def get_shipping_price_details(self):
        """Return details of shipping price as dict."""
        self.country = get_object_or_404(
            models.DestinationCountry, name=self.request.POST["country"]
        )
        weight = int(self.request.POST["weight"])
        price = int(self.request.POST["price"])
        self.exchange_rate = self.country.current_rate()
        postage_price = models.ShippingPrice.objects.get_price(
            self.country.name, self.package_type_name(), weight, price
        )
        vat_rates = list(postage_price.vat_rates.values())

        return self.format_response(
            success=True,
            price=postage_price.calculate(weight),
            price_name=postage_price.name,
            vat_rates=vat_rates,
            exchange_rate=self.exchange_rate,
            currency_code=self.country.currency_code,
            currency_symbol=self.country.currency_symbol,
            min_channel_fee=self.min_channel_fee(),
        )

    def no_shipping_price_response(self):
        """Return an invalid shipping service response as a JSON string."""
        return self.format_response(
            success=False, price_name="No Shipping Service Found"
        )

    def format_response(
        self,
        success=True,
        price=0,
        price_name="",
        vat_rates=[],
        exchange_rate=0,
        currency_code="GBP",
        currency_symbol="£",
        min_channel_fee=0,
    ):
        """Return shipping service information as a JSON string."""
        data = {
            self.SUCCESS: success,
            self.PRICE: price,
            self.PRICE_NAME: price_name,
            self.VAT_RATES: vat_rates,
            self.EXCHANGE_RATE: exchange_rate,
            self.CURRENCY_CODE: currency_code,
            self.CURRENCY_SYMBOL: currency_symbol,
            self.MIN_CHANNEL_FEE: min_channel_fee,
        }
        return json.dumps(data)


class RangePriceCalculatorView(InventoryUserMixin, TemplateView):
    """View calcualting prices for an existing Product Range."""

    template_name = "price_calculator/range_price_calculator.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        product_range = cc_products.get_range(self.kwargs.get("range_id"))
        context_data["product_range"] = product_range
        context_data["countries"] = models.DestinationCountry.objects.all()
        context_data["channel_fees"] = models.ChannelFee.objects.all()
        return context_data


class PriceCalculator(InventoryUserMixin, TemplateView):
    """View for using price calcualtor without an existing Product."""

    template_name = "price_calculator/price_calculator.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["countries"] = models.DestinationCountry.objects.all()
        context_data["package_types"] = models.PackageType.objects.all()
        context_data["channel_fees"] = models.ChannelFee.objects.all()
        return context_data
