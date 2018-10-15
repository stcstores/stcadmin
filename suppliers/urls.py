"""URL patterns for the Suppliers app."""

from django.urls import path
from suppliers import views

app_name = "suppliers"
urlpatterns = [
    path("supplier_search/", views.SupplierSearch.as_view(), name="supplier_search"),
    path("supplier/<int:pk>/", views.SupplierView.as_view(), name="supplier"),
    path(
        "supplier/<int:supplier_pk>/add_item/",
        views.CreateItem.as_view(),
        name="add_item_to_supplier",
    ),
    path("add_item/", views.CreateItem.as_view(), name="add_item"),
    path("add_item/", views.CreateItem.as_view(), name="add_item"),
    path("add_supplier/", views.CreateSupplier.as_view(), name="add_supplier"),
    path("delete_item/<int:item_id>/", views.DeleteItem.as_view(), name="delete_item"),
    path(
        "delete_supplier/<int:supplier_id>/",
        views.DeleteSupplier.as_view(),
        name="delete_supplier",
    ),
    path(
        "edit_supplier/<int:supplier_id>/",
        views.UpdateSupplier.as_view(),
        name="edit_supplier",
    ),
    path("api/export/", views.ApiExport.as_view(), name="api_export"),
    path(
        "api/get_item/<int:item_id>/", views.GetItemAJAX.as_view(), name="api_get_item"
    ),
    path(
        "api/update_item/<int:item_id>/",
        views.UpdateItemAJAX.as_view(),
        name="api_update_item",
    ),
    path(
        "api/delete_item/<int:item_id>/",
        views.DeleteItemAJAX.as_view(),
        name="api_delete_item",
    ),
    path("", views.Index.as_view(), name="index"),
]
