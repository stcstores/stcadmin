from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from epos import views

app_name = 'epos'

urlpatterns = [
    url(r'^index$', views.Index.as_view(), name='index'),
    url(
        r'^barcode_search$',
        views.BarcodeSearch.as_view(), name='barcode_search'),
    url(r'^epos_order$', views.EPOSOrder.as_view(), name='epos_order'),
    ]
