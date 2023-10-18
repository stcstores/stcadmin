import pytest_factoryboy

from inventory.factories import ProductFactory, SupplierFactory
from restock import factories

pytest_factoryboy.register(ProductFactory)
pytest_factoryboy.register(SupplierFactory)
pytest_factoryboy.register(factories.ReorderFactory)
pytest_factoryboy.register(factories.BlacklistedBrandFactory)
