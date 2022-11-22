import pytest_factoryboy

from home.factories import GroupFactory, UserFactory
from inventory.factories import SupplierFactory
from labelmaker import factories

pytest_factoryboy.register(UserFactory)
pytest_factoryboy.register(GroupFactory)
pytest_factoryboy.register(SupplierFactory)
pytest_factoryboy.register(factories.SizeChartFactory)
pytest_factoryboy.register(factories.SizeChartSizeFactory)
