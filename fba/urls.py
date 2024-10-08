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
    path("stopped", views.fba.StoppedFBAOrders.as_view(), name="stopped"),
    path(
        "price_calculator/",
        views.FBAPriceCalculatorView.as_view(),
        name="price_calculator",
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
    path(
        "stop_fba_order/<int:pk>",
        views.fba.StopFBAOrder.as_view(),
        name="stop_fba_order",
    ),
    path(
        "unstop_fba_order/<int:pk>",
        views.fba.UnstopFBAOrder.as_view(),
        name="unstop_fba_order",
    ),
    path("repeat_order/<int:pk>/", views.RepeatFBAOrder.as_view(), name="repeat_order"),
    path(
        "edit_tracking_numbers/<int:pk>/",
        views.EditTrackingNumbers.as_view(),
        name="edit_tracking_numbers",
    ),
    path("take_off_hold", views.TakeOffHold.as_view(), name="take_off_hold"),
    path("prioritise", views.PrioritiseOrder.as_view(), name="priortise_fba_order"),
    path(
        "shipping_calculator",
        views.fba.ShippingCalculator.as_view(),
        name="shipping_calculator",
    ),
    path("profit_list", views.FBAProfitList.as_view(), name="profit_list"),
    path(
        "product_profit/<int:pk>",
        views.FBAProductProfit.as_view(),
        name="product_profit",
    ),
    path("shipments", views.Shipments.as_view(), name="shipments"),
    path(
        "shipments/destinations",
        views.ShipmentDestinations.as_view(),
        name="shipment_destinations",
    ),
    path(
        "shipments/create_destination/",
        views.CreateDestination.as_view(),
        name="create_shipment_destination",
    ),
    path(
        "shipments/update_destination/<int:pk>/",
        views.UpdateDestination.as_view(),
        name="update_shipment_destination",
    ),
    path(
        "shipments/create_shipment_file/<int:fba_order_pk>/",
        views.CreateFBAShipmentFile.as_view(),
        name="create_shipment_file",
    ),
    path(
        "shipments/remove_destination/<int:pk>/",
        views.DisableDestination.as_view(),
        name="remove_destination",
    ),
    path(
        "shipments/create_shipment/select_destination",
        views.CreateShipment_SelectDestination.as_view(),
        name="create_shipment_select_destination",
    ),
    path(
        "shipments/create_shipment/create_destination",
        views.CreateShipment_CreateDestination.as_view(),
        name="create_shipment_create_destination",
    ),
    path(
        "shipments/create_shipment/<int:destination_pk>/",
        views.CreateShipment.as_view(),
        name="create_shipment",
    ),
    path(
        "shipments/update_shipment/<int:pk>/",
        views.UpdateShipment.as_view(),
        name="update_shipment",
    ),
    path(
        "shipments/create_package/<int:order_pk>",
        views.CreatePackage.as_view(),
        name="create_package",
    ),
    path(
        "shipments/update_package/<int:pk>",
        views.UpdatePackage.as_view(),
        name="update_package",
    ),
    path(
        "shipments/delete_package/<int:pk>",
        views.DeletePackage.as_view(),
        name="delete_package",
    ),
    path(
        "shipments/toggle_held/<int:pk>/",
        views.ToggleShipmentHeld.as_view(),
        name="toggle_shipment_held",
    ),
    path(
        "shipments/delete_shipment/<int:pk>/",
        views.DeleteShipment.as_view(),
        name="delete_shipment",
    ),
    path(
        "shipments/historic_shipments/",
        views.HistoricShipments.as_view(),
        name="historic_shipments",
    ),
    path(
        "shipments/file_parcelhub_shipment/<int:pk>",
        views.shipping.FileParcelhubShipment.as_view(),
        name="file_parcelhub_shipment",
    ),
    path(
        "shipments/file_parcelhub_shipment_status/<int:pk>",
        views.shipping.FileParcelhubShipmentStatus.as_view(),
        name="parcelhub_shipment_status",
    ),
    path(
        "get_stock_levels/", views.fba.GetStockLevels.as_view(), name="get_stock_levels"
    ),
    path(
        "shipments/clear_parcelhub_filing_error/<int:pk>",
        views.shipping.ClearParclhubFilingError.as_view(),
        name="clear_parcelhub_filing_error",
    ),
    path(
        "api/purchase_price_by_sku",
        views.api.PurchasePriceBySku.as_view(),
        name="purchase_price_by_sku",
    ),
]
