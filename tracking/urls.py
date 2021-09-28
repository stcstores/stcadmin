"""URLs for the tracking app."""

from django.urls import path

from tracking import views

app_name = "tracking"

urlpatterns = [
    path(
        "tracking_history/<str:tracking_number>/",
        views.TrackingHistory.as_view(),
        name="tracking_history",
    ),
    path(
        "update_tracking/<str:tracking_number>/",
        views.UpdateTracking.as_view(),
        name="update_tracking",
    ),
    path(
        "tracking_warnings", views.TrackingWarnings.as_view(), name="tracking_warnings"
    ),
]
