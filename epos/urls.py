from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from epos import views

app_name = 'epos'

urlpatterns = [
    url(
        r'^index$',
        views.index, name='index'),
        ]
