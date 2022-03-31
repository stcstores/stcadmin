import json
from unittest.mock import MagicMock

import pytest

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
def shipping_service(shipping_service_factory):
    return shipping_service_factory.create()


@pytest.fixture
def new_shipping_rule(rule_ID, name, courier_service):
    shipping_rule = models.ShippingRule(
        rule_ID=rule_ID, name=name, courier_service=courier_service
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
def test_default_shipping_service(new_shipping_rule):
    assert new_shipping_rule.shipping_service is None


@pytest.mark.django_db
def test_can_set_shipping_service(rule_ID, name, courier_service, shipping_service):
    shipping_rule = models.ShippingRule(
        rule_ID=rule_ID,
        name=name,
        courier_service=courier_service,
        shipping_service=shipping_service,
    )
    shipping_rule.save()
    assert shipping_rule.shipping_service == shipping_service


@pytest.mark.django_db
def test_str_method(shipping_rule_factory):
    shipping_rule = shipping_rule_factory.create()
    assert str(shipping_rule) == shipping_rule.name
