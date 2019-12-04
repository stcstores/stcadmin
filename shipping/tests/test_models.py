from decimal import Decimal

from shipping import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestCurrency(STCAdminTest):
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


class TestCountry(STCAdminTest):
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


class TestProvider(STCAdminTest):
    def test_create_object(self):
        name = "Test Provider"
        provider = models.Provider.objects.create(name=name)
        saved_provider = models.Provider.objects.get(id=provider.id)
        self.assertEqual(name, saved_provider.name)


class TestService(STCAdminTest):
    def test_create_object(self):
        name = "Test Service"
        provider = models.Provider.objects.create(name="Test Provider")
        service = models.Service.objects.create(name=name, provider=provider)
        self.assertEqual(name, service.name)
        self.assertEqual(provider, service.provider)


class TestShippingRule(STCAdminTest):
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
