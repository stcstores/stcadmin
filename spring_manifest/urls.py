from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

from spring_manifest import views

app_name = 'spring_manifest'

urlpatterns = [
    url(
        r'^index$', views.Index.as_view(),
        name='index'),
    url(
        r'^country_errors$', views.CountryErrors.as_view(),
        name='country_errors'),
    url(
        r'^spring_manifest$',
        views.SpringManifestView.as_view(), name='spring_manifest'),
    url(
        r'^spring_manifest_success$',
        views.SpringManifestSuccessView.as_view(),
        name='spring_manifest_success'),
]
