"""URLs for the linnworks app."""

from django.urls import path

from reports import views

app_name = "linnworks"

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("reorder_reports", views.ReorderReport.as_view(), name="reorder_reports"),
    path(
        "reorder_report/create",
        views.CreateReorderReport.as_view(),
        name="create_reorder_report",
    ),
    path(
        "reorder_report/list",
        views.ReorderReportList.as_view(),
        name="reorder_report_list",
    ),
    path(
        "reorder_report/status",
        views.ReorderReportStatus.as_view(),
        name="reorder_report_status",
    ),
]
