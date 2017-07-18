from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from inventory import views

app_name = 'inventory'

urlpatterns = [
    url(r'^index$', views.index, name='index'),
    url(r'^range_search$', views.range_search, name='range_search'),
    url(
        r'^product_range/(?P<range_id>[0-9]+)/$',
        views.product_range, name='product_range'),

]
