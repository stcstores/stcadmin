from django.conf.urls import include, url
from django.contrib import admin

from cloud_commerce import views

app_name = 'cloud_commerce'

urlpatterns = [
    url(
        r'^index$', views.index,
        name='index'),
    url(
        r'^stock_manager$', views.stock_manager,
        name='stock_manager'),

    url(
        r'^api/product_search/(?P<search_text>[\w\-]+)$',
        views.api_product_search, name='api_product_search'),

    url(
        r'^api/get_stock_for_products$',
        views.api_get_stock_for_product, name='api_get_stock_for_product'),

    url(
        r'^new_product$',
        views.new_product, name='new_product'),

    url(
        r'^new_single_product$',
        views.NewSingleProductView.as_view(), name='new_single_product'),

    url(
        r'^new_variation_product$',
        views.NewVariationProductView.as_view(), name='new_variation_product'),
]
