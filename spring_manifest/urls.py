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
        r'^manifest/(?P<manifest_id>[0-9]+)/$',
        views.ManifestView.as_view(), name='manifest'),
    url(
        r'^update_order/(?P<order_pk>[0-9]+)/$',
        views.UpdateOrderView.as_view(), name='update_order'),
    url(
        r'^spring_manifest_success$',
        views.SpringManifestSuccessView.as_view(),
        name='spring_manifest_success'),
    url(
        r'^manifest_list$',
        views.ManifestListView.as_view(),
        name='manifest_list'),
    url(
        r'^destination_zones$', views.DestinationZones.as_view(),
        name='destination_zones'),
]
