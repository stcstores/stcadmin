"""Views for price_calculator."""


from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from inventory.models import PackageType, ProductRange
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
        if response_data is None:
            return HttpResponse(status=500)
        return JsonResponse(response_data, safe=False)

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
        self.country = get_object_or_404(Country, id=self.request.POST["country"])
        try:
            weight = int(self.request.POST["weight"])
            price = int(self.request.POST["price"])
        except ValueError:
            return None
        self.exchange_rate = float(self.country.currency.exchange_rate())
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
        if self.country.vat_is_required() == Country.VAT_ALWAYS:
            rate = self.country.vat_rate()
            vat_rates = [{"name": f"Default VAT {rate}%", "percentage": rate}]
        elif self.country.vat_is_required() == Country.VAT_NEVER:
            vat_rates = [{"name": "VAT not applicable", "percentage": 0}]
        elif self.country.vat_is_required() == Country.VAT_VARIABLE:
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


class BasePriceCalculatorView(InventoryUserMixin, TemplateView):
    """Base view for price calculator pages."""

    def get_context_data(self, *args, **kwargs):
        """Get context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        country_ids = models.ShippingMethod.objects.values_list("country", flat=True)
        context_data["countries"] = Country.objects.filter(id__in=country_ids).order_by(
            "pk"
        )
        context_data["channel_fees"] = models.ChannelFee.objects.all()
        context_data["channels"] = models.Channel.objects.all()
        context_data["country_vat"] = self._get_country_vat(context_data["countries"])
        for country in context_data["countries"]:
            vat_required = country.vat_is_required()
            if vat_required == country.VAT_ALWAYS:
                context_data["country_vat"][country.name] = country.vat_rate()
            elif vat_required == country.VAT_NEVER:
                context_data["country_vat"][country.name] = 0
            else:
                context_data["country_vat"][country.name] = None
        return context_data

    def _get_country_vat(self, countries):
        vat = {}
        for country in countries:
            vat_required = country.vat_is_required()
            if vat_required == country.VAT_ALWAYS:
                vat[country.id] = country.vat_rate()
            elif vat_required == country.VAT_NEVER:
                vat[country.id] = 0
            else:
                vat[country.id] = None
        return vat


class RangePriceCalculatorView(BasePriceCalculatorView):
    """View calcualting prices for an existing Product Range."""

    template_name = "price_calculator/range_price_calculator.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data for template."""
        context = super().get_context_data(*args, **kwargs)
        product_range = get_object_or_404(ProductRange, pk=self.kwargs.get("range_pk"))
        context["product_range"] = product_range
        context["products"] = context["product_range"].products.variations().active()
        return context


class PriceCalculator(BasePriceCalculatorView):
    """View for using price calcualtor without an existing Product."""

    template_name = "price_calculator/price_calculator.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["product_types"] = models.ProductType.objects.all()
        return context_data
