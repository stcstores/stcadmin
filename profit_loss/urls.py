"""URL patterns for profit loss app."""

from django.urls import path

from profit_loss import views

app_name = "profit_loss"

urlpatterns = [
    path("orders", views.Orders.as_view(), name="orders"),
    path("order/<int:order_id>/", views.Order.as_view(), name="order"),
    path("export_orders", views.ExportOrders.as_view(), name="export_orders"),
]
