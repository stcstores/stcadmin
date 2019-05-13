"""URL patters for wowcher app."""

from django.urls import path

from wowcher import views

app_name = "wowcher"

urlpatterns = [
    path("", views.Orders.as_view(), name="orders"),
    path("redemption_file", views.GetRedemptionFile.as_view(), name="redemption_file"),
    path(
        "proof_of_delivery", views.ProofOfDelivery.as_view(), name="proof_of_delivery"
    ),
    path(
        "cancel_order/<int:order_ID>", views.CancelOrder.as_view(), name="cancel_order"
    ),
    path(
        "create_redemption_file",
        views.CreateRedemptionFile.as_view(),
        name="create_redemption_file",
    ),
    path(
        "download_redemption_file/<int:file_ID>",
        views.DownloadRedemptionFile.as_view(),
        name="download_redemption_file",
    ),
    path(
        "create_proof_of_delivery_file",
        views.CreateProofOfDeliveryFile.as_view(),
        name="create_proof_of_delivery_file",
    ),
    path(
        "download_proof_of_delivery_file/<int:file_ID>",
        views.DownloadProofOfDeliveryFile.as_view(),
        name="download_proof_of_delivery_file",
    ),
]
