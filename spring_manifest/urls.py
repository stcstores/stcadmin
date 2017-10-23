from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa
from spring_manifest import views

app_name = 'spring_manifest'

urlpatterns = [
    url(
        r'^index$', views.Index.as_view(),
        name='index'),
    url(
        r'^manifest/(?P<manifest_id>[0-9]+)/$',
        views.ManifestView.as_view(), name='manifest'),
    url(
        r'^file_manifest/(?P<manifest_id>[0-9]+)/$',
        views.FileManifestView.as_view(), name='file_manifest'),
    url(
        r'^update_order/(?P<order_pk>[0-9]+)/$',
        views.UpdateOrderView.as_view(), name='update_order'),
    url(
        r'^manifest_list$',
        views.ManifestListView.as_view(),
        name='manifest_list'),
    url(
        r'^canceled_orders$',
        views.CanceledOrdersView.as_view(),
        name='canceled_orders'),
]
