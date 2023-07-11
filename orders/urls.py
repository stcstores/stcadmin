"""URLs for the Orders app."""

from django.urls import path

from orders import views

app_name = "orders"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path(
        "pack_count_monitor/",
        views.PackCountMonitor.as_view(),
        name="pack_count_monitor",
    ),
    path("charts/", views.Charts.as_view(), name="charts"),
    path(
        "undispatched_data/",
        views.UndispatchedOrdersData.as_view(),
        name="undispatched_data",
    ),
    path(
        "undispatched_orders/",
        views.UndispatchedOrders.as_view(),
        name="undispatched_orders",
    ),
    path("order_list/", views.OrderList.as_view(), name="order_list"),
    path("export_orders/", views.ExportOrders.as_view(), name="export_orders"),
    path(
        "order_export_status",
        views.OrderExportStatus.as_view(),
        name="order_export_status",
    ),
    path(
        "order_profit/<int:order_id>/", views.OrderProfit.as_view(), name="order_profit"
    ),
]
