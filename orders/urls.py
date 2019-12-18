"""URLs for the home app."""

from django.urls import path

from orders import views

app_name = "home"
urlpatterns = [
    path(
        "pack_count_monitor/",
        views.PackCountMonitor.as_view(),
        name="pack_count_monitor",
    )
]
