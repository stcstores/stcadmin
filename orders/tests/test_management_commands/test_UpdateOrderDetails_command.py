from unittest.mock import Mock, patch

from orders.management import commands
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestUpdateOrderDetailsCommand(STCAdminTest):
    @patch("orders.management.commands.update_sale_details.OrderDetailsUpdate")
    def test_command(self, mock_order_details_update):
        commands.update_sale_details.Command().handle()
        mock_order_details_update.objects.start_update.assert_called_once()

    @patch("orders.management.commands.update_sale_details.OrderDetailsUpdate")
    def test_command_error(self, mock_order_details_update):
        mock_order_details_update.objects.start_update.side_effect = Mock(
            Exception("test")
        )
        with self.assertRaises(Exception):
            commands.update_sale_details.Command().handle()
        mock_order_details_update.objects.start_update.assert_called_once()
