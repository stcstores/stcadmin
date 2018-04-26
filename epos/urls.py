"""URLs for epos app."""

from django.urls import path

from epos import views

app_name = 'epos'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path(
        'barcode_search/',
        views.BarcodeSearch.as_view(), name='barcode_search'),
    path('epos_order/', views.EPOSOrder.as_view(), name='epos_order'),
]
