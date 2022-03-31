"""URLs for price_calculator."""

from django.urls import path

from price_calculator import views

app_name = "price_calculator"

urlpatterns = [
    path(
        "price_calculator/<int:range_pk>/",
        views.RangePriceCalculatorView.as_view(),
        name="range_price_calculator",
    ),
    path(
        "get_shipping_price/",
        views.GetShippingPrice.as_view(),
        name="get_shipping_price",
    ),
    path(
        "get_range_shipping_price/",
        views.GetRangeShippingPrice.as_view(),
        name="get_range_shipping_price",
    ),
    path("price_calculator/", views.PriceCalculator.as_view(), name="price_calculator"),
]
