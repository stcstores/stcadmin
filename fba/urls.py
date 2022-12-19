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
    path("take_off_hold", views.TakeOffHold.as_view(), name="take_off_hold"),
    path("prioritise", views.PrioritiseOrder.as_view(), name="priortise_fba_order"),
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
        "shipments/create_shipment_file/",
        views.CreateFBAShipmentFile.as_view(),
        name="create_shipment_file",
    ),
    path(
        "shipments/remove_destination/<int:pk>/",
        views.DisableDestination.as_view(),
        name="remove_destination",
    ),
    path(
        "shipments/create_shipment/select_destination/<int:fba_order_pk>/",
        views.CreateShipment_SelectDestination.as_view(),
        name="create_shipment_select_destination",
    ),
    path(
        "shipments/create_shipment/select_destination",
        views.CreateShipment_SelectDestination.as_view(),
        name="create_shipment_select_destination",
    ),
    path(
        "shipments/create_shipment/create_destination/<int:fba_order_pk>/",
        views.CreateShipment_CreateDestination.as_view(),
        name="create_shipment_create_destination",
    ),
    path(
        "shipments/create_shipment/create_destination",
        views.CreateShipment_CreateDestination.as_view(),
        name="create_shipment_create_destination",
    ),
    path(
        "shipments/create_shipment/<int:destination_pk>/<int:fba_order_pk>/",
        views.CreateShipment.as_view(),
        name="create_shipment",
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
        "shipments/download_shipment_file/<int:pk>/",
        views.DownloadFBAShipmentFile.as_view(),
        name="download_shipment_file",
    ),
    path(
        "shipments/download_address_file/<int:pk>/",
        views.DownloadUPSAddressFile.as_view(),
        name="download_address_file",
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
        "shipments/add_order_to_shipment/<int:fba_order_pk>/",
        views.AddFBAOrderToShipment.as_view(),
        name="add_fba_order_to_shipment",
    ),
    path(
        "shipments/add_order_packages_to_shipment/<int:fba_order_pk>/<int:shipment_pk>/",
        views.AddFBAOrderPackages.as_view(),
        name="add_order_packages_to_shipment",
    ),
    path(
        "get_stock_levels/", views.fba.GetStockLevels.as_view(), name="get_stock_levels"
    ),
    path(
        "api/current_shipments",
        views.api.CurrentShipments.as_view(),
        name="api_current_shipments",
    ),
    path(
        "api/shipment_exports",
        views.api.ShipmentExports.as_view(),
        name="api_shipment_exports",
    ),
    path(
        "api/download_shipment_file",
        views.api.DownloadShipmentFile.as_view(),
        name="api_download_shipment_file",
    ),
    path(
        "api/download_address_file",
        views.api.DownloadAddressFile.as_view(),
        name="api_download_address_file",
    ),
    path(
        "api/close_shipments",
        views.api.CloseShipments.as_view(),
        name="api_close_shipments",
    ),
]
