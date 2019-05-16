"""URL patters for wowcher app."""

from django.urls import path

from wowcher import views

app_name = "wowcher"

urlpatterns = [
    path("", views.Orders.as_view(), name="orders"),
    path("deals", views.Deals.as_view(), name="deals"),
    path(
        "delivery_status_file",
        views.GetDeliveryStatusFile.as_view(),
        name="delivery_status_file",
    ),
    path(
        "proof_of_delivery", views.ProofOfDelivery.as_view(), name="proof_of_delivery"
    ),
    path(
        "cancel_order/<int:order_ID>", views.CancelOrder.as_view(), name="cancel_order"
    ),
    path(
        "create_delivery_status_file",
        views.CreateDeliveryStatusFile.as_view(),
        name="create_delivery_status_file",
    ),
    path(
        "download_delivery_status_file/<int:file_ID>",
        views.DownloadDeliveryStatusFile.as_view(),
        name="download_delivery_status_file",
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
    path(
        "hide_stock_alert/<int:item_ID>",
        views.HideStockAlert.as_view(),
        name="hide_stock_alert",
    ),
    path("deal/<int:deal_id>", views.Deal.as_view(), name="deal"),
    path(
        "disable_deal/<int:deal_id>", views.DisableDeal.as_view(), name="disable_deal"
    ),
    path("enable_deal/<int:deal_id>", views.EnableDeal.as_view(), name="enable_deal"),
    path("end_deal/<int:deal_id>", views.EndDeal.as_view(), name="end_deal"),
]
