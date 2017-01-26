from django.conf.urls import url

from linnworks import views as linnworks_views

app_name = 'linnworks'

urlpatterns = [
    url(r'^$', linnworks_views.index, name='index'),
    url(r'^manifest/$', linnworks_views.manifest, name='manifest'),
    url(
        r'^cancel_consignment$', linnworks_views.cancel_consignment,
        name='cancel_consignment'),
    url(
        r'^sku_converter/$', linnworks_views.sku_converter,
        name='sku_converter'),
    url(
        r'^get_linked_for_channel_sku$',
        linnworks_views.get_linked_for_channel_sku,
        name='get_linked_for_channel_sku'),
    url(r'^new_item/$', linnworks_views.new_item, name='new_item'),
    url(
        r'^search_inventory/$', linnworks_views.search_inventory,
        name='search_inventory'),
    url(
        r'^inventory_item/(?P<stock_id>[0-9a-z-]+)/$',
        linnworks_views.inventory_item, name='inventory_item'),
]
