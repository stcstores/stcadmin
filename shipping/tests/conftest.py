import pytest_factoryboy

from shipping import factories

pytest_factoryboy.register(factories.CurrencyFactory)
pytest_factoryboy.register(factories.RegionFactory)
pytest_factoryboy.register(factories.CountryFactory)
pytest_factoryboy.register(factories.ProviderFactory)
pytest_factoryboy.register(factories.ShippingServiceFactory)
pytest_factoryboy.register(factories.ShippingPriceFactory)
pytest_factoryboy.register(factories.WeightBandFactory)
