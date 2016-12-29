from django.conf.urls import include, url
from django.contrib import admin

from reference import views

app_name = 'reference'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^shopify_tags$', views.shopify_tags, name='shopify_tags'),
]
