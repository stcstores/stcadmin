"""URLs for the channels app."""

from django.urls import path

from channels import views

app_name = "channels"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path(
        "create_order/channel_select/",
        views.CreateOrderChannelSelect.as_view(),
        name="create_order_channel_select",
    ),
    path(
        "create_order/<int:channel_pk>/",
        views.CreateOrder.as_view(),
        name="create_order",
    ),
    path(
        "created_order/<int:pk>",
        views.CreatedOrder.as_view(),
        name="created_order",
    ),
    path("import_orders/", views.ImportOrders.as_view(), name="import_orders"),
    path(
        "import_wish_orders/",
        views.ImportWishOrders.as_view(),
        name="import_wish_orders",
    ),
    path(
        "wish_import_results/<int:pk>/",
        views.WishImportResults.as_view(),
        name="wish_import_results",
    ),
    path(
        "wish_fulfilment_exports",
        views.WishFulfilmentExports.as_view(),
        name="wish_fulfilment_exports",
    ),
    path(
        "wish_fulfilment_export/<int:pk>/",
        views.WishFulfilmentExport.as_view(),
        name="wish_fulfilment_export",
    ),
    path(
        "create_new_wish_order_fulflment_file/",
        views.CreateNewWishOrderFulfilmentFile.as_view(),
        name="create_new_wish_order_fulflment_file",
    ),
    path(
        "wish_fulfilment_file_download/",
        views.DownloadWishfulfilmentFile.as_view(),
        name="wish_fulfilment_file_download",
    ),
    path(
        "mark_wish_order_unfulfiled/",
        views.MarkWishOrderUnfulfiled.as_view(),
        name="mark_wish_order_unfulfiled",
    ),
    path(
        "delay_wish_order_fulfilment/",
        views.DelayWishOrderFulfilment.as_view(),
        name="delay_wish_order_fulfilment",
    ),
    path(
        "wish_order_fulfilment_file_status/",
        views.WishOrderFulfilmentFileStatus.as_view(),
        name="wish_order_fulfilment_file_status",
    ),
]
