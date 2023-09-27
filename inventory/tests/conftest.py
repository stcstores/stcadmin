from pathlib import Path

import pytest
import pytest_factoryboy

from fba.factories import FBAOrderFactory
from inventory import factories

pytest_factoryboy.register(FBAOrderFactory)

pytest_factoryboy.register(factories.UserFactory)
pytest_factoryboy.register(factories.BarcodeFactory)
pytest_factoryboy.register(factories.PackageTypeFactory)
pytest_factoryboy.register(factories.BrandFactory)
pytest_factoryboy.register(factories.ManufacturerFactory)
pytest_factoryboy.register(factories.VATRateFactory)
pytest_factoryboy.register(factories.SupplierFactory)
pytest_factoryboy.register(factories.SupplierContactFactory)
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
def extra_image_paths():
    dir = Path(__file__).parent / "extra_images"
    names = [
        "0a34d5d5-57b5-4195-bd94-4f254d46c9cc.jpg",
        "0a8ff78d-2415-41cb-840d-cba35a2e4efe.jpg",
        "0a8ac9cc-6371-4229-9028-7685e5399a6d.jpg",
        "0a9de011-2499-4375-9e20-54e4eafbeaa3.jpg",
        "0a30a7b9-84e5-4b53-a21f-b5eeb4e6e5e5.jpg",
    ]
    return [dir / name for name in names]


@pytest.fixture
def test_image_hash():
    return "fc1173420074919f7b1fb9e293afcdd7"
