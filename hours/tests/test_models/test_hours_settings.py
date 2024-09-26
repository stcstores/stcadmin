import pytest


@pytest.fixture
def hours_settings(hours_settings_factory):
    return hours_settings_factory.create()


@pytest.mark.django_db
def test_hours_settings_has_send_report_to_attribute(hours_settings):
    assert isinstance(hours_settings.send_report_to, str)
