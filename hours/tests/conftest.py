import pytest_factoryboy

from hours import factories

pytest_factoryboy.register(factories.StaffFactory)

pytest_factoryboy.register(factories.HoursSettingsFactory)
pytest_factoryboy.register(factories.HoursExportFactory)
pytest_factoryboy.register(factories.ClockTimeFactory)
