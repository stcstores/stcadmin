from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from cloud_commerce import views

app_name = 'cloud_commerce'

urlpatterns = [
    url(
        r'^index$', views.Index.as_view(),
        name='index'),
    url(
        r'^spring_manifest$',
        views.SpringManifestView.as_view(), name='spring_manifest'),
    url(
        r'^spring_manifest_success$',
        views.SpringManifestSuccessView.as_view(),
        name='spring_manifest_success'),
]
