from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from epos import views

app_name = 'epos'

urlpatterns = [
    url(r'^index$', views.index, name='index'),
    url(r'^barcode_search$', views.barcode_search, name='barcode_search'),
    url(r'^epos_order$', views.epos_order, name='epos_order'),
    ]
