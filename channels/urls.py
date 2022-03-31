"""URLs for the channels app."""

from django.urls import path

from channels import views

app_name = "channels"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
]
