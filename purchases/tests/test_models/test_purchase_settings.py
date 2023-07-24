from decimal import Decimal

import pytest


@pytest.fixture
def purchase_settings(purchase_settings_factory):
    return purchase_settings_factory.create()


@pytest.mark.django_db
def test_purchase_settings_has_purchase_charge_attribute(purchase_settings):
    assert isinstance(purchase_settings.purchase_charge, Decimal)


@pytest.mark.django_db
def test_purchase_settings_has_send_report_to_attribute(purchase_settings):
    assert isinstance(purchase_settings.send_report_to, str)
