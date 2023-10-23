"""URLs for the restock app."""

from django.urls import path

from restock import views

app_name = "restock"

urlpatterns = [
    path("", views.RestockView.as_view(), name="restock"),
    path(
        "restock_results",
        views.SearchResults.as_view(),
        name="restock_results",
    ),
    path("restock_list", views.RestockList.as_view(), name="restock_list"),
    path(
        "restock_list/<int:supplier_pk>",
        views.SupplierRestockList.as_view(),
        name="supplier_restock_list",
    ),
    path(
        "update_purchase_price",
        views.UpdatePurchasePrice.as_view(),
        name="update_purchase_price",
    ),
    path(
        "update_order_count",
        views.UpdateOrderCount.as_view(),
        name="update_order_count",
    ),
    path(
        "set_order_comment", views.SetOrderComment.as_view(), name="set_order_comment"
    ),
    path("brand_blacklist", views.BrandBlacklist.as_view(), name="brand_blacklist"),
    path(
        "create_blacklisted_brand",
        views.CreateBlacklistedBrand.as_view(),
        name="create_blacklisted_brand",
    ),
    path(
        "update_blacklisted_brand/<int:pk>",
        views.UpdateBlacklistedBrand.as_view(),
        name="update_blacklisted_brand",
    ),
    path(
        "delete_blacklisted_brand/<int:pk>",
        views.DeleteBlacklistedBrand.as_view(),
        name="delete_blacklisted_brand",
    ),
    path(
        "update_supplier_last_order_date/<int:pk>",
        views.UpdateLastOrderedDate.as_view(),
        name="update_supplier_last_order_date",
    ),
]
