import pytest_factoryboy

from fba import factories

pytest_factoryboy.register(factories.FBARegionFactory)
pytest_factoryboy.register(factories.FBAOrderFactory)
