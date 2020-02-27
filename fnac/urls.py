"""URLs for the fnac app."""

from django.urls import path

from fnac import views

app_name = "fnac"
urlpatterns = [path("", views.Index.as_view(), name="index")]
