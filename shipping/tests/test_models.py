import json
import tempfile
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import override_settings

from shipping import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestCurrency(STCAdminTest):
    fixtures = ("shipping/currency",)

    def test_create_object(self):
        name = "Test Country Dollars"
        code = "TCD"
        exchange_rate = 1.275
        currency = models.Currency.objects.create(
            name=name, code=code, exchange_rate=exchange_rate
        )
        self.assertEqual(name, currency.name)
        self.assertEqual(code, currency.code)
        self.assertEqual(Decimal(float(exchange_rate)), currency.exchange_rate)

    def test_str_(self):
        currency = models.Currency.objects.get(id=1)
        self.assertEqual(currency.name, str(currency))

    @patch("shipping.models.requests.get")
    def test_update(self, mock_get):
        rates = {currency.code: 5 for currency in models.Currency.objects.all()}
        data = {"rates": rates}
        response = MagicMock()
        response.json.return_value = data
        mock_get.return_value = response
        models.Currency.update()
        mock_get.assert_called_once_with(models.Currency.EXCHANGE_RATE_URL)
        response.raise_for_status.assert_called_once()
        response.json.assert_called_once()
        self.assertEqual(3, len(mock_get.mock_calls))
        for currency in models.Currency.objects.all():
            self.assertEqual(float(currency.exchange_rate), 1 / 5)


class TestCountry(STCAdminTest):
    fixtures = ("shipping/currency", "shipping/country")

    def test_create_object(self):
        country_ID = "839"
        name = "Test Country"
        ISO_code = "TC"
        region = models.Country.EU
        currency = models.Currency.objects.create(
            name="Test Country Dollars", code="TCD", exchange_rate=1.2
        )
        country = models.Country.objects.create(
            country_ID="839",
            name="Test Country",
            region=models.Country.EU,
            currency=currency,
            ISO_code=ISO_code,
        )
        self.assertEqual(country_ID, country.country_ID)
        self.assertEqual(name, country.name)
        self.assertEqual(ISO_code, country.ISO_code)
        self.assertEqual(region, country.region)
        self.assertEqual(currency, country.currency)

    def test_str(self):
        country = models.Country.objects.get(id=1)
        self.assertEqual(country.name, str(country))


class TestProvider(STCAdminTest):
    fixtures = ("shipping/currency", "shipping/country", "shipping/provider")

    def test_create_object(self):
        name = "Test Provider"
        provider = models.Provider.objects.create(name=name)
        saved_provider = models.Provider.objects.get(id=provider.id)
        self.assertEqual(name, saved_provider.name)

    def test_str(self):
        provider = models.Provider.objects.get(id=1)
        self.assertEqual(provider.name, str(provider))


class TestCourierType(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
    )

    def test_create_object(self):
        courier_type_ID = "202"
        name = "New Courier Type"
        provider = models.Provider.objects.get(id=1)
        courier_type = models.CourierType.objects.create(
            courier_type_ID=courier_type_ID, name=name, provider=provider
        )
        self.assertEqual(courier_type_ID, courier_type.courier_type_ID)
        self.assertEqual(name, courier_type.name)
        self.assertEqual(provider, courier_type.provider)
        self.assertFalse(courier_type.inactive)

    def test_str(self):
        courier_type = models.CourierType.objects.get(id=1)
        self.assertEqual(courier_type.name, str(courier_type))


class TestCourier(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
    )

    def test_create_object(self):
        courier_ID = "1493"
        name = "New Courier"
        courier_type = models.CourierType.objects.get(id=1)
        courier = models.Courier.objects.create(
            courier_type=courier_type, name=name, courier_ID=courier_ID
        )
        self.assertEqual(courier_ID, courier.courier_ID)
        self.assertEqual(name, courier.name)
        self.assertEqual(courier_type, courier.courier_type)
        self.assertFalse(courier.inactive)

    def test_str(self):
        courier = models.Courier.objects.get(id=1)
        self.assertEqual(f"{courier.courier_ID}: {courier.name}", str(courier))

    def test_create_with_nulls(self):
        courier_ID = "1493"
        courier = models.Courier.objects.create(courier_ID=courier_ID)
        self.assertEqual(courier_ID, courier.courier_ID)
        self.assertIsNone(courier.name)
        self.assertIsNone(courier.courier_type)
        self.assertFalse(courier.inactive)


class TestCourierService(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
        "shipping/courier_service",
    )

    def test_create_object(self):
        courier_service_ID = "28493"
        name = "New Courier Service"
        courier = models.Courier.objects.get(id=1)
        courier_service = models.CourierService.objects.create(
            courier_service_ID=courier_service_ID, name=name, courier=courier
        )
        self.assertEqual(courier_service_ID, courier_service.courier_service_ID)
        self.assertEqual(name, courier_service.name)
        self.assertEqual(courier, courier_service.courier)
        self.assertFalse(courier_service.inactive)

    def test_str(self):
        courier_service = models.CourierService.objects.get(id=1)
        self.assertEqual(
            f"{courier_service.courier_service_ID}: {courier_service.name}",
            str(courier_service),
        )

    def test_create_with_nulls(self):
        courier_service_ID = "28493"
        courier_service = models.CourierService.objects.create(
            courier_service_ID=courier_service_ID
        )
        self.assertEqual(courier_service_ID, courier_service.courier_service_ID)
        self.assertIsNone(courier_service.name)
        self.assertIsNone(courier_service.courier)
        self.assertFalse(courier_service.inactive)


class TestShippingRule(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
        "shipping/courier_service",
        "shipping/shipping_rule",
    )

    def mock_cc_rule(
        self,
        rule_ID,
        name="Mock Rule",
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

    def mock_rules(self, rules, json=None):
        if json is None:
            json = []
        mock_rules = MagicMock(json=json)
        mock_rules.__iter__.return_value = rules
        return mock_rules

    def test_create_object(self):
        courier_service = models.CourierService.objects.create(name="Test Service")
        name = "Test Shipping Rule"
        rule_ID = "38493"
        shipping_rule = models.ShippingRule.objects.create(
            name=name, rule_ID=rule_ID, courier_service=courier_service
        )
        self.assertEqual(name, shipping_rule.name)
        self.assertEqual(rule_ID, shipping_rule.rule_ID)
        self.assertEqual(courier_service, shipping_rule.courier_service)
        self.assertFalse(shipping_rule.priority)
        self.assertFalse(shipping_rule.inactive)

    def test_str(self):
        rule = models.ShippingRule.objects.get(id=1)
        self.assertEqual(rule.name, str(rule))

    @patch("shipping.models.CCAPI")
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_update_marks_inactive(self, mock_CCAPI):
        models.ShippingRule.objects.filter(id__gt=1).delete()
        models.ShippingRule.objects.update(inactive=False)
        mock_CCAPI.get_courier_rules.return_value = self.mock_rules([])
        models.ShippingRule.update()
        mock_CCAPI.get_courier_rules.assert_called_once()
        self.assertTrue(models.ShippingRule.objects.get(id=1).inactive)

    @patch("shipping.models.CCAPI")
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_update_marks_active(self, mock_CCAPI):
        models.ShippingRule.objects.filter(id__gt=1).delete()
        models.ShippingRule.objects.update(inactive=True)
        rule = models.ShippingRule.objects.get(id=1)
        cc_rule = self.mock_cc_rule(rule_ID=rule.rule_ID)
        mock_CCAPI.get_courier_rules.return_value = self.mock_rules([cc_rule])
        models.ShippingRule.update()
        mock_CCAPI.get_courier_rules.assert_called_once()
        rule.refresh_from_db()
        self.assertFalse(rule.inactive)

    @patch("shipping.models.CCAPI")
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_update_creates_rule(self, mock_CCAPI):
        rule_ID = "948416"
        self.assertFalse(models.ShippingRule.objects.filter(rule_ID=rule_ID).exists())
        cc_rule = self.mock_cc_rule(rule_ID=rule_ID)
        mock_CCAPI.get_courier_rules.return_value = self.mock_rules([cc_rule])
        models.ShippingRule.update()
        mock_CCAPI.get_courier_rules.assert_called_once()
        self.assertTrue(models.ShippingRule.objects.filter(rule_ID=rule_ID).exists())
        rule = models.ShippingRule.objects.get(rule_ID=rule_ID)
        self.assertEqual(cc_rule.name, rule.name)
        self.assertIsNotNone(rule.courier_service)
        self.assertEqual(bool(cc_rule.is_priority), rule.priority)
        self.assertFalse(rule.inactive)

    @patch("shipping.models.CCAPI")
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_update_uses_existing_courier_service(self, mock_CCAPI):
        rule_ID = "948416"
        models.ShippingRule.objects.all().delete()
        courier_service = models.CourierService.objects.get(id=1)
        cc_rule = self.mock_cc_rule(
            rule_ID=rule_ID,
            courier_ID=courier_service.courier.courier_ID,
            courier_service_ID=courier_service.courier_service_ID,
        )
        mock_CCAPI.get_courier_rules.return_value = self.mock_rules([cc_rule])
        models.ShippingRule.update()
        mock_CCAPI.get_courier_rules.assert_called_once()
        self.assertTrue(models.ShippingRule.objects.filter(rule_ID=rule_ID).exists())
        rule = models.ShippingRule.objects.get(rule_ID=rule_ID)
        self.assertEqual(courier_service, rule.courier_service)

    @patch("shipping.models.CCAPI")
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_backup_file_saved(self, mock_CCAPI):
        cc_rule = self.mock_cc_rule(rule_ID="981684")
        data = {"Shipping Rule": cc_rule.name}
        mock_CCAPI.get_courier_rules.return_value = self.mock_rules(
            [cc_rule], json=data
        )
        models.ShippingRule.update()
        file_path = models.ShippingRule._backup_path()
        self.assertTrue(file_path.exists)
        with open(file_path) as f:
            saved_data = json.load(f)
        self.assertDictEqual(data, saved_data)

    @patch("shipping.models.CCAPI")
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_update_creates_new_courier_service(self, mock_CCAPI):
        rule_ID = "948416"
        models.ShippingRule.objects.all().delete()
        courier_service_ID = "956816"
        courier_ID = "9548"
        self.assertFalse(
            models.CourierService.objects.filter(
                courier_service_ID=courier_service_ID
            ).exists()
        )
        self.assertFalse(models.Courier.objects.filter(courier_ID=courier_ID).exists())
        cc_rule = self.mock_cc_rule(
            rule_ID=rule_ID,
            courier_ID=courier_ID,
            courier_service_ID=courier_service_ID,
        )
        mock_CCAPI.get_courier_rules.return_value = self.mock_rules([cc_rule])
        models.ShippingRule.update()
        mock_CCAPI.get_courier_rules.assert_called_once()
        self.assertTrue(models.ShippingRule.objects.filter(rule_ID=rule_ID).exists())
        rule = models.ShippingRule.objects.get(rule_ID=rule_ID)
        self.assertTrue(models.Courier.objects.filter(courier_ID=courier_ID).exists())
        courier = models.Courier.objects.get(courier_ID=courier_ID)
        self.assertIsNone(courier.name)
        self.assertIsNone(courier.courier_type)
        self.assertFalse(courier.inactive)
        self.assertTrue(
            models.CourierService.objects.filter(
                courier_service_ID=courier_service_ID
            ).exists()
        )
        courier_service = models.CourierService.objects.get(
            courier_service_ID=courier_service_ID
        )
        self.assertIsNone(courier_service.name)
        self.assertEqual(courier, courier_service.courier)
        self.assertFalse(courier_service.inactive)
        self.assertEqual(courier_service, rule.courier_service)
