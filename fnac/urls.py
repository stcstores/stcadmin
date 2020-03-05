"""URLs for the fnac app."""

from django.urls import path

from fnac import views

app_name = "fnac"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path(
        "missing_inventory_info/",
        views.MissingInventoryInfo.as_view(),
        name="missing_inventory_info",
    ),
]
