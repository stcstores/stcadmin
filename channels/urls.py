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
]
