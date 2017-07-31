from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from print_audit import views

app_name = 'print_audit'

urlpatterns = [
    url(r'^index$', views.index, name='index'),

    url(
        r'^display_monitor$',
        views.display_monitor, name='display_monitor'),

]
