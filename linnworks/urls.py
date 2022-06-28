"""URLs for the linnworks app."""

from django.urls import path

from linnworks import views

app_name = "linnworks"

urlpatterns = [
    path("get_stock_levels/", views.get_stock_levels, name="get_stock_levels"),
    path("update_stock_levels/", views.update_stock_levels, name="update_stock_levels"),
    path(
        "get_initial_stock_levels/",
        views.get_initial_stock_levels,
        name="get_initial_stock_levels",
    ),
    path(
        "update_initial_stock_levels/",
        views.update_initial_stock_levels,
        name="update_initial_stock_levels",
    ),
    path("stock_record/", views.get_stock_records, name="stock_record"),
    path(
        "stock_level_hisotry/<int:product_pk>/",
        views.StockLevelHistory.as_view(),
        name="stock_level_hisotry",
    ),
    path("stock_value", views.StockValue.as_view(), name="stock_value"),
]
