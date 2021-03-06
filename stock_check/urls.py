"""URL patterns for the Stock Check app."""

from django.urls import path

from stock_check import views

app_name = "stock_check"

urlpatterns = [
    path("product_search/", views.ProductSearch.as_view(), name="product_search"),
    path("warehouses/", views.Warehouses.as_view(), name="warehouses"),
    path("warehouse/<int:warehouse_ID>/", views.Warehouse.as_view(), name="warehouse"),
    path("bay/<int:bay_ID>/", views.Bay.as_view(), name="bay"),
    path(
        "update_stock_check_level/",
        views.UpdateStockCheckLevel.as_view(),
        name="update_stock_check_level",
    ),
    path(
        "open_orders/<int:bay_ID>/", views.AjaxOpenOrders.as_view(), name="open_orders"
    ),
]
