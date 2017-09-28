from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from inventory import views

app_name = 'inventory'

inventory_urlpatterns = [
    url(r'^index$', views.IndexView.as_view(), name='index'),
    url(
        r'^product_search$',
        views.ProductSearchView.as_view(), name='product_search'),
    url(
        r'^product_range/(?P<range_id>[0-9]+)/$',
        views.ProductRangeView.as_view(), name='product_range'),
    url(
        r'^locations/(?P<range_id>[0-9]+)/',
        views.LocationFormView.as_view(), name='locations'),
    url(
        r'^variations/(?P<range_id>[0-9]+)/',
        views.VariationsFormView.as_view(), name='variations'),
    url(
        r'^images/(?P<range_id>[0-9]+)/',
        views.ImageFormView.as_view(), name='images'),
    url(
        r'^product/(?P<product_id>[0-9]+)/$',
        views.ProductView.as_view(), name='product'),
    url(
        r'^descriptions/(?P<range_id>[0-9]+)/$',
        views.DescriptionsView.as_view(), name='descriptions'),
    url(
        r'^sku_generator$',
        views.SKUGeneratorView.as_view(), name='sku_generator'),
]

new_product_urlpatterns = [
    url(
        r'^new_product$',
        views.NewProductView.as_view(), name='new_product'),
    url(
        r'^new_single_product$',
        views.NewSingleProductView.as_view(), name='new_single_product'),
    url(
        r'^new_variation_product$',
        views.VariationFormWizardView.as_view(), name='new_variation_product'),

]

api_urlpatterns = [
    url(
        r'^get_stock_for_products$',
        views.GetStockForProductView.as_view(), name='get_stock_for_product'),
    url(
        r'^get_new_sku$',
        views.GetNewSKUView.as_view(), name='get_new_sku'),
    url(
        r'^get_new_range_sku$',
        views.GetNewRangeSKUView.as_view(), name='get_new_range_sku'),
    url(
        r'^update_stock_level$',
        views.UpdateStockLevelView.as_view(), name='update_stock_level'),
]

urlpatterns = inventory_urlpatterns + new_product_urlpatterns + api_urlpatterns
