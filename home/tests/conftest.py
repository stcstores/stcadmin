import pytest_factoryboy

from home import factories

pytest_factoryboy.register(factories.UserFactory)
pytest_factoryboy.register(factories.StaffFactory)
pytest_factoryboy.register(factories.GroupFactory)
pytest_factoryboy.register(factories.ExternalLinkFactory)
