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
    path("refund_list/", views.RefundList.as_view(), name="refund_list"),
    path("create_refund/", views.CreateRefund.as_view(), name="create_refund"),
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
    path(
        "refund/add_images/<int:refund_pk>/",
        views.AddRefundImages.as_view(),
        name="add_refund_images",
    ),
    path(
        "refund/add_images/<int:refund_pk>/<int:product_pk>/",
        views.AddRefundImages.as_view(),
        name="add_refund_images",
    ),
    path(
        "refund/delete_image/<int:pk>/",
        views.DeleteRefundImage.as_view(),
        name="delete_refund_image",
    ),
    path(
        "refund/<int:pk>/set_notes/",
        views.SetRefundNotes.as_view(),
        name="set_refund_notes",
    ),
    path("export_refunds/", views.ExportRefunds.as_view(), name="export_refunds"),
    path(
        "refund/<int:refund_pk>/create_feedback/",
        views.AddPackingMistakeForRefund.as_view(),
        name="add_packing_mistake_feedback",
    ),
    path(
        "refund/<int:refund_pk>/delete_refund/",
        views.DeleteRefund.as_view(),
        name="delete_refund",
    ),
    path(
        "refund/<int:refund_pk>/set_returned/",
        views.SetParcelReturnedForRefund.as_view(),
        name="set_refund_parcel_returned",
    ),
    path(
        "refund/<int:refund_pk>/set_not_returned/",
        views.SetParcelNotReturnedForRefund.as_view(),
        name="set_refund_parcel_not_returned",
    ),
    path(
        "refund/<int:refund_pk>/mark_refund_parital",
        views.MarkRefundPartial.as_view(),
        name="mark_refund_parital",
    ),
]
