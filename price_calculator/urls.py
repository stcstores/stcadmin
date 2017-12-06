from django.urls import path
from price_calculator import views

app_name = 'price_calculator'

urlpatterns = [
    path(
        'price_calculator/<int:range_id>/',
        views.RangePriceCalculatorView.as_view(),
        name='range_price_calculator'),
    path(
        'get_shipping_price/',
        views.GetShippingPriceView.as_view(), name='get_shipping_price'),
    path(
        'price_calculator/',
        views.PriceCalculator.as_view(), name='price_calculator'),
]
