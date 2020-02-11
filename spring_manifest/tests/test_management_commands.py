from unittest.mock import Mock, patch

from spring_manifest.management import commands
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestUpdateManifest(STCAdminTest):
    @patch("spring_manifest.management.commands.update_manifest.update_manifest_orders")
    def test_update_manifest(self, mock_update_manifest_orders):
        commands.update_manifest.Command().handle()
        mock_update_manifest_orders.assert_called_once()

    @patch("spring_manifest.management.commands.update_manifest.update_manifest_orders")
    def test_update_manifest_error(self, mock_update_manifest_orders):
        mock_update_manifest_orders.side_effect = Mock(Exception("test"))
        with self.assertRaises(Exception):
            commands.update_manifest.Command().handle()
        mock_update_manifest_orders.assert_called_once()
