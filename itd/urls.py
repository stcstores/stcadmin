"""URLs for the ITD app."""

from django.urls import path

from itd import views

app_name = "itd"

urlpatterns = [
    path("", views.ITDManifest.as_view(), name="itd_manifest"),
    path("manifest_list/", views.ITDManifestList.as_view(), name="manifest_list"),
    path("create_manifest/", views.CreateITDManifest.as_view(), name="create_manifest"),
]
