from unittest.mock import patch

from shipping.management import commands
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestUpdateExchangeRates(STCAdminTest):
    fixtures = ("shipping/currency",)

    @patch("shipping.management.commands.update_exchange_rates.Currency")
    def test_update(self, mock_currency):
        commands.update_exchange_rates.Command().handle()
        mock_currency.objects.update_rates.assert_called_once()
        self.assertEqual(1, len(mock_currency.mock_calls))

    @patch("shipping.management.commands.update_exchange_rates.Currency")
    def test_error(self, mock_currency):
        mock_currency.objects.update_rates.side_effect = Exception()
        with self.assertRaises(Exception):
            commands.update_exchange_rates.Command().handle()
        mock_currency.objects.update_rates.assert_called_once()
        self.assertEqual(1, len(mock_currency.mock_calls))


class TestUpdateShippingRules(STCAdminTest):
    @patch("shipping.management.commands.update_shipping_rules.ShippingRule")
    def test_update(self, mock_ShippingRule):
        commands.update_shipping_rules.Command().handle()
        mock_ShippingRule.objects.update_rules.assert_called_once()
        self.assertEqual(1, len(mock_ShippingRule.mock_calls))

    @patch("shipping.management.commands.update_shipping_rules.ShippingRule")
    def test_error(self, mock_ShippingRule):
        mock_ShippingRule.objects.update_rules.side_effect = Exception()
        with self.assertRaises(Exception):
            commands.update_shipping_rules.Command().handle()
        mock_ShippingRule.objects.update_rules.assert_called_once()
        self.assertEqual(1, len(mock_ShippingRule.mock_calls))
