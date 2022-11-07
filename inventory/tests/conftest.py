from pathlib import Path

import pytest
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
pytest_factoryboy.register(factories.ProductImageFactory)
pytest_factoryboy.register(factories.ProductImageLinkFactory)
pytest_factoryboy.register(factories.ProductRangeImageLinkFactory)


@pytest.fixture
def test_image_path():
    return Path(__file__).parent / "test_image.jpg"


@pytest.fixture
def test_image_hash():
    return "fc1173420074919f7b1fb9e293afcdd7"
