from django.conf.urls import url

from suppliers import views

app_name = 'suppliers'
urlpatterns = [
    url(
        r'^supplier_search/$', views.supplier_search,
        name='supplier_search'),
    url(
        r'^supplier/(?P<supplier_id>[0-9]+)/$', views.supplier,
        name='supplier'),
    url(
        r'^supplier/(?P<supplier_id>[0-9]+)/add_item/$',
        views.add_item_to_supplier, name='add_item'),
    url(r'^add_item/$', views.add_item, name='add_item'),
    url(r'^create_item/$', views.create_item, name='create_item'),
    url(r'^add_supplier/$', views.add_supplier, name='add_supplier'),
    url(
        r'^api/create_supplier/$', views.create_supplier,
        name='create_supplier'),
    url(
        r'^delete_item/(?P<item_id>[0-9]+)/$', views.delete_item,
        name='delete_item'),
    url(
        r'^delete_supplier/(?P<supplier_id>[0-9]+)/$', views.delete_supplier,
        name='delete_supplier'),
    url(
        r'^api/get_item/(?P<item_id>[0-9]+)/$', views.api_get_item,
        name='api_get_item'),
    url(
        r'^api/update_item/(?P<item_id>[0-9]+)/$', views.api_update_item,
        name='api_update_item'),
    url(
        r'^api/delete_item/(?P<item_id>[0-9]+)/$', views.api_delete_item,
        name='api_delete_item'),
    url(
        r'^edit_supplier/(?P<supplier_id>[0-9]+)/$', views.edit_supplier,
        name='edit_supplier'),
    url(r'^api/export/$', views.ApiExport.as_view, name='api_export'),
    url(r'^', views.index, name='index'),
]
