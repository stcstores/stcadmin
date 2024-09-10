"""URLs for the Hours app."""

from django.urls import path

from hours import views

app_name = "hours"

urlpatterns = [
    path("hours", views.Hours.as_view(), name="hours"),
    path("clock", views.Clock.as_view(), name="clock"),
    path("clocked_too_soon", views.ClockedTooSoon.as_view(), name="clocked_too_soon"),
    path("update_hours/<str:date>", views.UpdateHours.as_view(), name="update_hours"),
]
