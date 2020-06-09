"""Views for price_calculator."""

import cc_products
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from inventory.models import PackageType
from inventory.views.views import InventoryUserMixin
from price_calculator import models
from shipping.models import Country


class GetShippingPrice(InventoryUserMixin, View):
    """View for AJAX requests for shipping prices."""

    SUCCESS = "success"
    PRICE = "price"
    PRICE_NAME = "price_name"
    VAT_RATES = "vat_rates"
    EXCHANGE_RATE = "exchange_rate"
    CURRENCY_CODE = "currency_code"
    CURRENCY_SYMBOL = "currency_symbol"
    MIN_CHANNEL_FEE = "min_channel_fee"
    CHANNEL = "channel"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Mark view as CSRF exempt."""
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Return shipping prices as JSON or return server error."""
        try:
            response_data = self.get_shipping_price_details()
        except models.NoShippingService:
            response_data = self.no_shipping_price_response()
        return JsonResponse(response_data)

    def product_type(self):
        """Return the package type."""
        return models.ProductType.objects.get(name=self.request.POST["package_type"])

    def channel(self):
        """Return the selected channel."""
        channel_name = self.request.POST[self.CHANNEL]
        if channel_name != "":
            return models.Channel.objects.get(name=channel_name)
        return None

    def min_channel_fee(self):
        """Return the minimum channel fee."""
        try:
            min_fee = models.CountryChannelFee.objects.get(
                country=self.country
            ).min_channel_fee
        except models.CountryChannelFee.DoesNotExist:
            return 0
        else:
            return int(min_fee * self.exchange_rate)

    def get_shipping_price_details(self):
        """Return details of shipping price as dict."""
        self.country = get_object_or_404(Country, name=self.request.POST["country"])
        weight = int(self.request.POST["weight"])
        price = int(self.request.POST["price"])
        self.exchange_rate = float(self.country.currency.exchange_rate)
        (
            shipping_method,
            shipping_price,
        ) = models.ShippingMethod.objects.get_shipping_price(
            country=self.country,
            product_type=self.product_type(),
            channel=self.channel(),
            weight=weight,
            price=price,
        )
        vat_rates = list(shipping_method.vat_rates.values())
        return self.format_response(
            success=True,
            price=shipping_price,
            price_name=shipping_method.name,
            vat_rates=vat_rates,
            exchange_rate=self.exchange_rate,
            currency_code=self.country.currency.code,
            currency_symbol=self.country.currency.symbol,
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
        vat_rates=None,
        exchange_rate=0,
        currency_code="GBP",
        currency_symbol="£",
        min_channel_fee=0,
    ):
        """Return shipping service information as a JSON string."""
        if vat_rates is None:
            vat_rates = []
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
        return data


class GetRangeShippingPrice(GetShippingPrice):
    """View for AJAX shipping price requests for Product Ranges."""

    def product_type(self):
        """Return the package type."""
        if self.country.region.name == "UK":
            package_type = PackageType.objects.get(
                name=self.request.POST["package_type"]
            )
            return models.ProductType.objects.get(package_types=package_type)
        try:
            return models.ProductType.objects.get(
                name=self.request.POST["international_shipping"]
            )
        except models.ProductType.DoesNotExist:
            return models.ProductType.objects.get(
                name=self.request.POST["package_type"]
            )


class RangePriceCalculatorView(InventoryUserMixin, TemplateView):
    """View calcualting prices for an existing Product Range."""

    template_name = "price_calculator/range_price_calculator.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        product_range = cc_products.get_range(self.kwargs.get("range_id"))
        context_data["product_range"] = product_range
        country_ids = models.ShippingMethod.objects.values_list("country", flat=True)
        context_data["countries"] = Country.objects.filter(id__in=country_ids)
        context_data["channel_fees"] = models.ChannelFee.objects.all()
        context_data["channels"] = models.Channel.objects.all()
        return context_data


class PriceCalculator(InventoryUserMixin, TemplateView):
    """View for using price calcualtor without an existing Product."""

    template_name = "price_calculator/price_calculator.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        country_ids = models.ShippingMethod.objects.values_list("country", flat=True)
        context_data["countries"] = Country.objects.filter(id__in=country_ids)
        context_data["product_types"] = models.ProductType.objects.all()
        context_data["channel_fees"] = models.ChannelFee.objects.all()
        context_data["channels"] = models.Channel.objects.all()
        return context_data
