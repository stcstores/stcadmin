"""URLs for the Orders app."""

from django.urls import path

from orders import views

app_name = "orders"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
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
    path("pack_count", views.PackCount.as_view(), name="pack_count"),
    path(
        "pack_count_results",
        views.PackCountResults.as_view(),
        name="pack_count_results",
    ),
    path("packing_mistakes", views.PackingMistakes.as_view(), name="packing_mistakes"),
    path(
        "create_packing_mistake",
        views.CreatePackingMistake.as_view(),
        name="create_packing_mistake",
    ),
    path(
        "update_packing_mistake/<int:pk>",
        views.UpdatePackingMistake.as_view(),
        name="update_packing_mistake",
    ),
    path(
        "delete_packing_mistake/<int:pk>",
        views.DeletePackingMistake.as_view(),
        name="delete_packing_mistake",
    ),
]
