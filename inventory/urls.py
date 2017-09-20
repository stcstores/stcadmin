from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from inventory import views

app_name = 'inventory'

urlpatterns = [
    url(r'^index$', views.Index.as_view(), name='index'),
    url(r'^range_search$', views.RangeSearch.as_view(), name='range_search'),
    url(
        r'^product_range/(?P<range_id>[0-9]+)/$',
        views.ProductRange.as_view(), name='product_range'),
    url(
        r'^locations/(?P<range_id>[0-9]+)/',
        views.LocationForm.as_view(), name='locations'),
    url(
        r'^images/(?P<range_id>[0-9]+)/',
        views.ImageForm.as_view(), name='images'),
    url(
        r'^product/(?P<product_id>[0-9]+)/$',
        views.Product.as_view(), name='product'),
    url(
        r'^descriptions/(?P<range_id>[0-9]+)/$',
        views.Descriptions.as_view(), name='descriptions'),
    url(
        r'^new_product$',
        views.NewProduct.as_view(), name='new_product'),
    url(
        r'^new_single_product$',
        views.NewSingleProductView.as_view(), name='new_single_product'),
    url(
        r'^new_variation_product$',
        views.VariationFormWizard.as_view(), name='new_variation_product'),
    url(
        r'^sku_generator$',
        views.SKUGenerator.as_view(), name='sku_generator'),
]
