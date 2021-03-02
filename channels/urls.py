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
]
