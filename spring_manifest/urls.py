"""URL patters for manifest app."""

from django.urls import path

from spring_manifest import views

app_name = "spring_manifest"

urlpatterns = [
    path("manifest/<int:manifest_id>/", views.ManifestView.as_view(), name="manifest"),
    path(
        "file_manifest/<int:manifest_id>/",
        views.FileManifestView.as_view(),
        name="file_manifest",
    ),
    path(
        "update_order/<int:order_pk>/",
        views.UpdateOrderView.as_view(),
        name="update_order",
    ),
    path("manifest_list/", views.ManifestListView.as_view(), name="manifest_list"),
    path(
        "split_order/<int:order_pk>/",
        views.SplitOrderView.as_view(),
        name="split_order",
    ),
    path(
        "canceled_orders/", views.CanceledOrdersView.as_view(), name="canceled_orders"
    ),
    path("order_exists/", views.OrderExists.as_view(), name="order_exists"),
    path("update_manifest/", views.UpdateManifest.as_view(), name="update_manifest"),
    path(
        "send_secured_mail_manifest_files/",
        views.SendSecuredMailManifest.as_view(),
        name="send_secured_mail_manifest_files",
    ),
]
