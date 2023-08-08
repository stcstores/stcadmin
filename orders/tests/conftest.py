import pytest_factoryboy

from home.factories import StaffFactory
from inventory.factories import SupplierFactory
from orders import factories
from shipping.factories import (
    CountryFactory,
    ProviderFactory,
    ShippingPriceFactory,
    ShippingServiceFactory,
    WeightBandFactory,
)

pytest_factoryboy.register(CountryFactory)
pytest_factoryboy.register(ShippingServiceFactory)
pytest_factoryboy.register(ShippingPriceFactory)
pytest_factoryboy.register(WeightBandFactory)
pytest_factoryboy.register(ProviderFactory)
pytest_factoryboy.register(StaffFactory)
pytest_factoryboy.register(SupplierFactory)
pytest_factoryboy.register(factories.ChannelFactory)
pytest_factoryboy.register(factories.OrderFactory)
pytest_factoryboy.register(factories.ProductSaleFactory)
