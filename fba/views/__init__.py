"""Views for the fba app."""

from . import api
from .fba import (
    Awaitingfulfillment,
    DeleteFBAOrder,
    EditTrackingNumbers,
    FBAOrderCreate,
    FBAOrderPrintout,
    FBAOrderUpdate,
    FBAPriceCalculatorView,
    FBAProductProfit,
    FBAProfitList,
    FulfillFBAOrder,
    Index,
    OnHold,
    OrderList,
    PrioritiseOrder,
    RepeatFBAOrder,
    SelectFBAOrderProduct,
    TakeOffHold,
    UnmarkPrinted,
)
from .shipping import (
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
    "FBAPriceCalculatorView",
    "FBAProductProfit",
    "FBAProfitList",
    "FulfillFBAOrder",
    "Index",
    "OnHold",
    "OrderList",
    "PrioritiseOrder",
    "RepeatFBAOrder",
    "SelectFBAOrderProduct",
    "TakeOffHold",
    "UnmarkPrinted",
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
