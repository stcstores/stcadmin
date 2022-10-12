import pytest_factoryboy

from inventory import factories

pytest_factoryboy.register(factories.UserFactory)
pytest_factoryboy.register(factories.BarcodeFactory)
pytest_factoryboy.register(factories.PackageTypeFactory)
pytest_factoryboy.register(factories.BrandFactory)
pytest_factoryboy.register(factories.ManufacturerFactory)
pytest_factoryboy.register(factories.VATRateFactory)
pytest_factoryboy.register(factories.SupplierFactory)
pytest_factoryboy.register(factories.ProductRangeFactory)
pytest_factoryboy.register(factories.BaseProductFactory)
pytest_factoryboy.register(factories.ProductFactory)
pytest_factoryboy.register(factories.InitialVariationFactory)
pytest_factoryboy.register(factories.MultipackProductFactory)
pytest_factoryboy.register(factories.CombinationProductFactory)
pytest_factoryboy.register(factories.CombinationProductLinkFactory)
pytest_factoryboy.register(factories.StockLevelHistoryFactory)
pytest_factoryboy.register(factories.BayFactory)
pytest_factoryboy.register(factories.ProductBayLinkFactory)
pytest_factoryboy.register(factories.ProductBayHistoryFactory)
pytest_factoryboy.register(factories.VariationOptionFactory)
pytest_factoryboy.register(factories.ListingAttributeFactory)
pytest_factoryboy.register(factories.VariationOptionValueFactory)
pytest_factoryboy.register(factories.ListingAttributeValueFactory)
