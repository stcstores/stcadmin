"""URLs for print audit app."""

from django.urls import path

from print_audit import views

app_name = "print_audit"

urlpatterns = [
    path("index/", views.Index.as_view(), name="index"),
    path("charts/", views.Charts.as_view(), name="charts"),
    path("breakages/", views.BreakageIndex.as_view(), name="breakages"),
    path("add_breakage/", views.AddBreakage.as_view(), name="add_breakage"),
    path(
        "update_breakage/<int:breakage_id>/",
        views.UpdateBreakage.as_view(),
        name="update_breakage",
    ),
    path(
        "delete_breakage/<int:breakage_id>/",
        views.DeleteBreakage.as_view(),
        name="delete_breakage",
    ),
]
