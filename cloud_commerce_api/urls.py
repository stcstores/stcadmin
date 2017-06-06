from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from cloud_commerce_api import views

app_name = 'cloud_commerce'

urlpatterns = [
    url(
        r'^product_search/(?P<search_text>.+?)$',
        views.product_search, name='product_search'),

    url(
        r'^get_stock_for_products$',
        views.get_stock_for_product, name='get_stock_for_product'),

    url(
        r'^get_new_sku$',
        views.get_new_sku, name='get_new_sku'),

    url(
        r'^get_new_range_sku$',
        views.get_new_range_sku, name='get_new_range_sku'),

    url(
        r'^update_stock_level$',
        views.update_stock_level, name='update_stock_level'),
]
