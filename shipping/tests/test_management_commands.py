from unittest.mock import patch

from shipping.management import commands
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestUpdateExchangeRates(STCAdminTest):
    fixtures = ("shipping/currency",)

    @patch("shipping.management.commands.update_exchange_rates.Currency")
    def test_update(self, mock_currency):
        commands.update_exchange_rates.Command().handle()
        mock_currency.update.assert_called_once()
        self.assertEqual(1, len(mock_currency.mock_calls))

    @patch("shipping.management.commands.update_exchange_rates.Currency")
    def test_error(self, mock_currency):
        mock_currency.update.side_effect = Exception()
        with self.assertRaises(Exception):
            commands.update_exchange_rates.Command().handle()
        mock_currency.update.assert_called_once()
        self.assertEqual(1, len(mock_currency.mock_calls))
