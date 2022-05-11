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
]
