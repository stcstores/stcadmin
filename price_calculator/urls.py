from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from price_calculator import views

app_name = 'price_calculator'

urlpatterns = [
    url(
        r'^price_calculator/(?P<range_id>[0-9]+)/',
        views.RangePriceCalculatorView.as_view(),
        name='range_price_calculator'),
    url(
        r'^get_shipping_price$',
        views.GetShippingPriceView.as_view(), name='get_shipping_price'),
    url(
        r'^price_calculator/$',
        views.PriceCalculator.as_view(), name='price_calculator'),
]
