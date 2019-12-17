"""URLs for print audit app."""

from django.urls import path

from monitor import views

app_name = "monitor"

urlpatterns = [
    path("", views.DisplayMonitor.as_view(), name="monitor"),
    path(
        "pack_count_monitor/",
        views.PackCountMonitor.as_view(),
        name="pack_count_monitor",
    ),
]
