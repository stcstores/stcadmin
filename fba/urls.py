"""URLs for the FBA app."""

from django.urls import path

from fba import views

app_name = "fba"

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path(
        "select_product_for_order",
        views.SelectFBAOrderProduct.as_view(),
        name="select_product_for_order",
    ),
    path(
        "create_order/<int:product_id>/",
        views.FBAOrderCreate.as_view(),
        name="create_order",
    ),
    path(
        "update_order/<int:pk>/",
        views.FBAOrderUpdate.as_view(),
        name="update_fba_order",
    ),
    path("fba_order_list/", views.OrderList.as_view(), name="order_list"),
    path(
        "awaiting_fulillment/",
        views.Awaitingfulfillment.as_view(),
        name="awaiting_fulfillment",
    ),
    path("on_hold/", views.OnHold.as_view(), name="on_hold"),
    path(
        "price_calculator/", views.FBAPriceCalculator.as_view(), name="price_calculator"
    ),
    path(
        "fulfill_fba_order/<int:pk>/",
        views.FulfillFBAOrder.as_view(),
        name="fulfill_fba_order",
    ),
    path(
        "order_printout/<int:pk>/",
        views.FBAOrderPrintout.as_view(),
        name="order_printout",
    ),
    path(
        "unmark_printed/<int:pk>/", views.UnmarkPrinted.as_view(), name="unmark_printed"
    ),
    path("delete_order/<int:pk>/", views.DeleteFBAOrder.as_view(), name="delete_order"),
    path("repeat_order/<int:pk>/", views.RepeatFBAOrder.as_view(), name="repeat_order"),
    path(
        "shipping_price/<int:pk>/", views.ShippingPrice.as_view(), name="shipping_price"
    ),
    path(
        "set_tracking_number/",
        views.SetTrackingNumber.as_view(),
        name="set_tracking_number",
    ),
    path("product_stock", views.ProductStock.as_view(), name="product_stock"),
    path("take_off_hold", views.TakeOffHold.as_view(), name="take_off_hold"),
    path(
        "create_fulfillment_center",
        views.CreateFulfillemntCenter.as_view(),
        name="create_fulfillment_center",
    ),
    path(
        "update_fulfillment_center/<int:pk>/",
        views.UpdateFulfillmentCenter.as_view(),
        name="update_fulfillment_center",
    ),
    path(
        "delete_fulfillment_center/<int:pk>/",
        views.DeleteFulfillmentCenter.as_view(),
        name="delete_fulfillment_center",
    ),
    path(
        "fulfillment_center",
        views.FulfillmentCenterList.as_view(),
        name="fulfillment_center_list",
    ),
    path("invoice/<int:pk>/", views.FBAInvoice.as_view(), name="invoice"),
    path("prioritise", views.PrioritiseOrder.as_view(), name="priortise_fba_order"),
]
