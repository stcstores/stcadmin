from unittest.mock import Mock, patch

from orders.management import commands
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestUpdateOrdersCommand(STCAdminTest):
    from orders.management.commands.update_orders import Command

    @patch("orders.management.commands.update_orders.OrderUpdate")
    def test_command(self, mock_order_update):
        commands.update_orders.Command().handle()
        mock_order_update.objects.start_order_update.assert_called_once()

    @patch("orders.management.commands.update_orders.OrderUpdate")
    def test_command_error(self, mock_order_update):
        mock_order_update.objects.start_order_update.side_effect = Mock(
            Exception("test")
        )
        with self.assertRaises(Exception):
            commands.update_orders.Command().handle()
        mock_order_update.objects.start_order_update.assert_called_once()
