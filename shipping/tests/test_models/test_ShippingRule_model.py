import json
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from shipping import models


@pytest.fixture
def rule_ID():
    return "10056"


@pytest.fixture
def name():
    return "Test Courier Service"


@pytest.fixture
def courier_service(courier_service_factory):
    return courier_service_factory.create()


@pytest.fixture
def new_shipping_rule(rule_ID, name, courier_service):
    shipping_rule = models.ShippingRule(
        rule_ID=rule_ID, name=name, courier_service=courier_service,
    )
    shipping_rule.save()
    return shipping_rule


@pytest.fixture
def mock_cc_rule():
    def _mock_cc_rule(
        rule_ID="48328",
        name="Test Shipping Rule",
        priority=False,
        courier_ID="57",
        courier_service_ID="2564",
    ):
        mock_rule = MagicMock(
            id=rule_ID,
            is_priority=int(priority),
            courier_services_group_id=courier_ID,
            courier_services_rule_id=courier_service_ID,
        )
        mock_rule.name = name
        return mock_rule

    return _mock_cc_rule


@pytest.fixture
def mock_cc_rules():
    def _mock_cc_rules(rules):
        rules_json = [
            {
                "ID": rule.id,
                "RuleName": rule.name,
                "IsPriority": rule.is_priority,
                "CourierServicesGroupID": rule.courier_services_group_id,
                "CourierServicesRuleId": rule.courier_services_rule_id,
            }
            for rule in rules
        ]
        mock_rules = MagicMock(json=json.dumps(rules_json))
        mock_rules.__iter__.return_value = rules
        return mock_rules

    return _mock_cc_rules


@pytest.fixture
def mock_get_courier_rules():
    with patch("shipping.models.CCAPI.get_courier_rules") as mock_get_courier_rules:
        yield mock_get_courier_rules


@pytest.mark.django_db
def test_rule_ID_is_set(rule_ID, new_shipping_rule):
    assert new_shipping_rule.rule_ID == rule_ID


@pytest.mark.django_db
def test_name_is_set(name, new_shipping_rule):
    assert new_shipping_rule.name == name


@pytest.mark.django_db
def test_courier_service_is_set(courier_service, new_shipping_rule):
    assert new_shipping_rule.courier_service == courier_service


@pytest.mark.django_db
def test_priority_is_set(new_shipping_rule):
    assert new_shipping_rule.priority is False


@pytest.mark.django_db
def test_inactive_is_set(new_shipping_rule):
    assert new_shipping_rule.inactive is False


@pytest.mark.django_db
def test_str_method(shipping_rule_factory):
    shipping_rule = shipping_rule_factory.create()
    assert str(shipping_rule) == shipping_rule.name


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_update_marks_inactive(
    mock_get_courier_rules, mock_cc_rules, shipping_rule_factory
):
    shipping_rule = shipping_rule_factory.create(inactive=False)
    mock_get_courier_rules.return_value = mock_cc_rules([])
    models.ShippingRule.update()
    shipping_rule.refresh_from_db()
    assert shipping_rule.inactive is True


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_update_marks_active(
    mock_get_courier_rules, mock_cc_rule, mock_cc_rules, shipping_rule_factory
):
    shipping_rule = shipping_rule_factory.create(inactive=True)
    mock_rule = mock_cc_rule(rule_ID=shipping_rule.rule_ID)
    mock_get_courier_rules.return_value = mock_cc_rules([mock_rule])
    models.ShippingRule.update()
    shipping_rule.refresh_from_db()
    assert shipping_rule.inactive is False


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_update_creates_rule(
    rule_ID,
    mock_get_courier_rules,
    mock_cc_rule,
    mock_cc_rules,
    courier_service_factory,
):
    courier_service = courier_service_factory.create()
    mock_rule = mock_cc_rule(
        rule_ID=rule_ID,
        courier_ID=courier_service.courier.courier_ID,
        courier_service_ID=courier_service.courier_service_ID,
    )
    mock_get_courier_rules.return_value = mock_cc_rules([mock_rule])
    models.ShippingRule.update()
    shipping_rule = models.ShippingRule.objects.get(rule_ID=rule_ID)
    assert shipping_rule.courier_service == courier_service
    assert shipping_rule.name == mock_rule.name


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_update_creates_a_shipping_rule_backup(
    mock_get_courier_rules, mock_cc_rule, mock_cc_rules
):
    mock_rules = mock_cc_rules(mock_cc_rule())
    mock_get_courier_rules.return_value = mock_rules
    models.ShippingRule.update()
    file_path = models.ShippingRule._backup_path()
    with open(file_path) as f:
        saved_data = json.load(f)
    assert mock_rules.json == saved_data


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_update_creates_courier_service(
    rule_ID, mock_get_courier_rules, mock_cc_rule, mock_cc_rules, courier_factory
):
    courier_service_ID = "94984"
    courier = courier_factory.create()
    mock_rule = mock_cc_rule(
        courier_ID=courier.courier_ID, courier_service_ID=courier_service_ID
    )
    mock_get_courier_rules.return_value = mock_cc_rules([mock_rule])
    models.ShippingRule.update()
    courier_service = models.CourierService.objects.get(
        courier_service_ID=courier_service_ID
    )
    assert courier_service.name is None
    assert courier_service.courier == courier
    assert courier_service.inactive is False
