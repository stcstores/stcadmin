from django.urls import path
from suppliers import views

app_name = 'suppliers'
urlpatterns = [
    path(
        'supplier_search/', views.supplier_search,
        name='supplier_search'),
    path(
        'supplier/<int:supplier_id>/', views.supplier,
        name='supplier'),
    path(
        'supplier/<int:supplier_id>/add_item/',
        views.add_item_to_supplier, name='add_item'),
    path('add_item/', views.add_item, name='add_item'),
    path('create_item/', views.create_item, name='create_item'),
    path('add_supplier/', views.add_supplier, name='add_supplier'),
    path(
        'api/create_supplier/', views.create_supplier,
        name='create_supplier'),
    path(
        'delete_item/<int:item_id>/', views.delete_item,
        name='delete_item'),
    path(
        'delete_supplier/<int:supplier_id>/', views.delete_supplier,
        name='delete_supplier'),
    path(
        'api/get_item/<int:item_id>/', views.api_get_item,
        name='api_get_item'),
    path(
        'api/update_item/<int:item_id>/', views.api_update_item,
        name='api_update_item'),
    path(
        'api/delete_item/<int:item_id>/', views.api_delete_item,
        name='api_delete_item'),
    path(
        'edit_supplier/<int:supplier_id>/', views.edit_supplier,
        name='edit_supplier'),
    path('api/export/', views.ApiExport.as_view, name='api_export'),
    path('', views.index, name='index'),
]
