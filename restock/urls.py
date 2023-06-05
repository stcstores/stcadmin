"""URLs for the restock app."""

from django.urls import path

from restock import views

app_name = "restock"

urlpatterns = [
    path("", views.RestockView.as_view(), name="restock"),
    path(
        "search_results",
        views.SearchResults.as_view(),
        name="restock_results",
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
]
