import pytest_factoryboy

from fba import factories
from home.factories import StaffFactory, UserFactory
from inventory.factories import (
    CombinationProductLinkFactory,
    MultipackProductFactory,
    ProductBayLinkFactory,
    ProductFactory,
    SupplierFactory,
)

pytest_factoryboy.register(factories.FBARegionFactory)
pytest_factoryboy.register(factories.FBAOrderFactory)
pytest_factoryboy.register(factories.FBATrackingNumberFactory)
pytest_factoryboy.register(factories.ShipmentConfigFactory)
pytest_factoryboy.register(factories.FBAShipmentDestinationFactory)
pytest_factoryboy.register(factories.FBAShipmentExportFactory)
pytest_factoryboy.register(factories.FBAShipmentMethodFactory)
pytest_factoryboy.register(factories.FBAShipmentOrderFactory)
pytest_factoryboy.register(factories.FBAShipmentPackageFactory)
pytest_factoryboy.register(factories.FBAShipmentItemFactory)
pytest_factoryboy.register(UserFactory)
pytest_factoryboy.register(StaffFactory)
pytest_factoryboy.register(ProductFactory)
pytest_factoryboy.register(MultipackProductFactory)
pytest_factoryboy.register(CombinationProductLinkFactory)
pytest_factoryboy.register(SupplierFactory)
pytest_factoryboy.register(ProductBayLinkFactory)
