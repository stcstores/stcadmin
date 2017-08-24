from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from cloud_commerce import views

app_name = 'cloud_commerce'

urlpatterns = [
    url(
        r'^index$', views.index,
        name='index'),

    url(
        r'^new_product$',
        views.new_product, name='new_product'),

    url(
        r'^new_single_product$',
        views.NewSingleProductView.as_view(), name='new_single_product'),

    url(
        r'^new_variation_product$',
        views.VariationFormWizard.as_view(), name='new_variation_product'),

    url(
        r'^sku_generator$',
        views.sku_generator, name='sku_generator'),

    url(
        r'^product_range/(?P<range_id>[0-9]+)/$',
        views.product_range, name='product_range'),

    url(
        r'^spring_manifest$',
        views.SpringManifestView.as_view(), name='spring_manifest'),

    url(
        r'^spring_manifest_success$',
        views.SpringManifestSuccessView.as_view(),
        name='spring_manifest_success'),

]
