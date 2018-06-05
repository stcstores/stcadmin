"""URL patterns for the reference app."""

from django.urls import path

from reference import views

app_name = 'reference'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
]
