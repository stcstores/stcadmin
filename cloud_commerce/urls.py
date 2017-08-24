from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from cloud_commerce import views

app_name = 'cloud_commerce'

urlpatterns = [
    url(
        r'^index$', views.Index.as_view(),
        name='index'),

    url(
        r'^new_product$',
        views.NewProduct.as_view(), name='new_product'),

    url(
        r'^new_single_product$',
        views.NewSingleProductView.as_view(), name='new_single_product'),

    url(
        r'^new_variation_product$',
        views.VariationFormWizard.as_view(), name='new_variation_product'),

    url(
        r'^sku_generator$',
        views.SKUGenerator.as_view(), name='sku_generator'),

    url(
        r'^spring_manifest$',
        views.SpringManifestView.as_view(), name='spring_manifest'),

    url(
        r'^spring_manifest_success$',
        views.SpringManifestSuccessView.as_view(),
        name='spring_manifest_success'),

]
