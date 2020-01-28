from decimal import Decimal
from unittest.mock import Mock, patch

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
        response = Mock()
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


class TestService(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "shipping/provider",
        "shipping/service",
    )

    def test_create_object(self):
        name = "Test Service"
        provider = models.Provider.objects.create(name="Test Provider")
        service = models.Service.objects.create(name=name, provider=provider)
        self.assertEqual(name, service.name)
        self.assertEqual(provider, service.provider)

    def test_str(self):
        service = models.Service.objects.get(id=1)
        self.assertEqual(service.name, str(service))


class TestShippingRule(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "shipping/provider",
        "shipping/service",
        "shipping/shipping_rule",
    )

    def test_create_object(self):
        provider = models.Provider.objects.create(name="Test Provider")
        service = models.Service.objects.create(name="Test Service", provider=provider)
        name = "Test Shipping Rule"
        rule_ID = "38493"
        shipping_rule = models.ShippingRule.objects.create(
            name=name, rule_ID=rule_ID, service=service
        )
        self.assertEqual(name, shipping_rule.name)
        self.assertEqual(rule_ID, shipping_rule.rule_ID)
        self.assertEqual(service, shipping_rule.service)
        self.assertFalse(shipping_rule.priority)
        self.assertFalse(shipping_rule.inactive)

    def test_str(self):
        rule = models.ShippingRule.objects.get(id=1)
        self.assertEqual(rule.name, str(rule))
