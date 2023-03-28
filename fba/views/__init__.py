"""Views for the fba app."""
from . import api
from .fba import (
    Awaitingfulfillment,
    DeleteFBAOrder,
    EditTrackingNumbers,
    FBAOrderCreate,
    FBAOrderPrintout,
    FBAOrderUpdate,
    FBAPriceCalculator,
    FulfillFBAOrder,
    Index,
    OnHold,
    OrderList,
    PrioritiseOrder,
    RepeatFBAOrder,
    SelectFBAOrderProduct,
    ShippingPrice,
    TakeOffHold,
    UnmarkPrinted,
)
from .shipping import (
    AddFBAOrderPackages,
    AddFBAOrderToShipment,
    CreateDestination,
    CreateFBAShipmentFile,
    CreatePackage,
    CreateShipment,
    CreateShipment_CreateDestination,
    CreateShipment_SelectDestination,
    DeletePackage,
    DeleteShipment,
    DisableDestination,
    DownloadFBAShipmentFile,
    DownloadUPSAddressFile,
    HistoricShipments,
    ShipmentDestinations,
    Shipments,
    ToggleShipmentHeld,
    UpdateDestination,
    UpdatePackage,
    UpdateShipment,
)

__all__ = [
    "api",
    "Awaitingfulfillment",
    "DeleteFBAOrder",
    "EditTrackingNumbers",
    "FBAOrderCreate",
    "FBAOrderPrintout",
    "FBAOrderUpdate",
    "FBAPriceCalculator",
    "FulfillFBAOrder",
    "Index",
    "OnHold",
    "OrderList",
    "PrioritiseOrder",
    "RepeatFBAOrder",
    "SelectFBAOrderProduct",
    "ShippingPrice",
    "TakeOffHold",
    "UnmarkPrinted",
    "AddFBAOrderPackages",
    "AddFBAOrderToShipment",
    "CreateDestination",
    "CreateFBAShipmentFile",
    "CreatePackage",
    "CreateShipment",
    "CreateShipment_CreateDestination",
    "CreateShipment_SelectDestination",
    "DeletePackage",
    "DeleteShipment",
    "DisableDestination",
    "DownloadFBAShipmentFile",
    "DownloadUPSAddressFile",
    "HistoricShipments",
    "ShipmentDestinations",
    "Shipments",
    "ToggleShipmentHeld",
    "UpdateDestination",
    "UpdatePackage",
    "UpdateShipment",
]
