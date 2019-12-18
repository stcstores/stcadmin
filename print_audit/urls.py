"""URLs for print audit app."""

from django.urls import path

from print_audit import views

app_name = "print_audit"

urlpatterns = [
    path("index/", views.Index.as_view(), name="index"),
    path("charts/", views.Charts.as_view(), name="charts"),
]
