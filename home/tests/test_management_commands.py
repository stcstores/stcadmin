from unittest.mock import Mock, patch

from home import models
from home.management import commands
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestUpdateCloudCommerceUsers(STCAdminTest):
    fixtures = ("home/cloud_commerce_user",)

    @patch("home.management.commands.update_cloud_commerce_users.CCAPI")
    def test_command(self, mock_CCAPI):
        first_name = "Joe"
        second_name = "Bob"
        mock_CCAPI.get_users.return_value = {
            user.user_id: Mock(
                user_id=user.user_id, first_name=first_name, second_name=second_name
            )
            for user in models.CloudCommerceUser.unhidden.all()
        }
        commands.update_cloud_commerce_users.Command().handle()
        mock_CCAPI.get_users.assert_called_once()
        for user in models.CloudCommerceUser.unhidden.all():
            self.assertEqual(first_name, user.first_name)
            self.assertEqual(second_name, user.second_name)
        self.assertEqual(1, len(mock_CCAPI.mock_calls))

    @patch("home.management.commands.update_cloud_commerce_users.CCAPI")
    def test_missing_user_id(self, mock_CCAPI):
        mock_CCAPI.get_users.return_value = {}
        commands.update_cloud_commerce_users.Command().handle()
        mock_CCAPI.get_users.assert_called_once()
        self.assertEqual(1, len(mock_CCAPI.mock_calls))

    @patch("home.management.commands.update_cloud_commerce_users.CCAPI")
    def test_first_name(self, mock_CCAPI):
        user = models.CloudCommerceUser.objects.get(id=1)
        mock_CCAPI.get_users.return_value = {
            user.user_id: Mock(first_name=None, second_name="Bob")
        }
        commands.update_cloud_commerce_users.Command().handle()
        original_name = user.first_name
        user.refresh_from_db()
        self.assertEqual(user.first_name, original_name)
        mock_CCAPI.get_users.assert_called_once()
        self.assertEqual(1, len(mock_CCAPI.mock_calls))

    @patch("home.management.commands.update_cloud_commerce_users.CCAPI")
    def test_second_name(self, mock_CCAPI):
        user = models.CloudCommerceUser.objects.get(id=1)
        mock_CCAPI.get_users.return_value = {
            user.user_id: Mock(first_name="Jone", second_name=None)
        }
        commands.update_cloud_commerce_users.Command().handle()
        original_name = user.second_name
        user.refresh_from_db()
        self.assertEqual(user.second_name, original_name)
        mock_CCAPI.get_users.assert_called_once()
        self.assertEqual(1, len(mock_CCAPI.mock_calls))

    @patch("home.management.commands.update_cloud_commerce_users.CCAPI")
    def test_CCAPI_exception_raised(self, mock_CCAPI):
        mock_CCAPI.get_users.return_value = Mock(Exception("test"))
        with self.assertRaises(Exception):
            commands.update_cloud_commerce_users.Command().handle()
        mock_CCAPI.get_users.assert_called_once()
        self.assertEqual(1, len(mock_CCAPI.mock_calls))
