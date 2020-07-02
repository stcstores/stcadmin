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
    path("breakages/", views.BreakageIndex.as_view(), name="breakages"),
    path("add_breakage/", views.AddBreakage.as_view(), name="add_breakage"),
    path(
        "update_breakage/<int:breakage_id>/",
        views.UpdateBreakage.as_view(),
        name="update_breakage",
    ),
    path(
        "delete_breakage/<int:breakage_id>/",
        views.DeleteBreakage.as_view(),
        name="delete_breakage",
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
        "order_profit/<int:order_id>/", views.OrderProfit.as_view(), name="order_profit"
    ),
    path("refund_list/", views.RefundList.as_view(), name="refund_list"),
    path("create_refund/", views.CreateRefund.as_view(), name="create_refund",),
    path("refund/<int:pk>/", views.Refund.as_view(), name="refund"),
    path(
        "refund/<int:pk>/mark_contacted/",
        views.MarkRefundContacted.as_view(),
        name="mark_refund_contacted",
    ),
    path(
        "refund/<int:pk>/mark_accepted/",
        views.MarkRefundAccepted.as_view(),
        name="mark_refund_accepted",
    ),
    path(
        "refund/<int:pk>/mark_rejected/",
        views.MarkRefundRejected.as_view(),
        name="mark_refund_rejected",
    ),
    path(
        "refund/select_products/<str:refund_type>/<int:order_pk>/",
        views.SelectRefundProducts.as_view(),
        name="select_refund_products",
    ),
]
