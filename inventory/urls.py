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
        r'^description_editor/(?P<range_id>[0-9]+)/$',
        views.DescriptionEditor.as_view(), name='description_editor'),
]
