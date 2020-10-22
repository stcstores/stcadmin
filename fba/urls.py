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
]
