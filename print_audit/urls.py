"""URLs for print audit app."""

from django.urls import path

from print_audit import views

app_name = "print_audit"

urlpatterns = [
    path("index/", views.Index.as_view(), name="index"),
    path("display_monitor/", views.DisplayMonitor.as_view(), name="display_monitor"),
    path(
        "pack_count_monitor/",
        views.PackCountMonitor.as_view(),
        name="pack_count_monitor",
    ),
    path("feedback_monitor/", views.FeedbackMonitor.as_view(), name="feedback_monitor"),
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
