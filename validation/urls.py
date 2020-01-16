"""URLs for the validation app."""

from django.urls import path

from validation import views

app_name = "validation"

urlpatterns = [
    path("home/", views.Home.as_view(), name="home"),
    path("app/<str:app>/", views.App.as_view(), name="app"),
    path("model/<str:app>/<str:model>/", views.Model.as_view(), name="model"),
]
