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
]
