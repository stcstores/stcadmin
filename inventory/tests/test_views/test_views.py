from unittest.mock import Mock, patch

from django.contrib.auth.models import Group
from django.shortcuts import reverse

from inventory import models, views
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class InventoryViewTest(STCAdminTest):
    group_name = "inventory"

    def setUp(self):
        self.create_user()
        group = Group.objects.get(name=self.group_name)
        group.user_set.add(self.user)
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


class TestInventoryUserMixin(STCAdminTest):
    def setUp(self):
        self.create_user()
        self.add_group("inventory")
        self.login_user()

    def test_valid_group(self):
        view = views.InventoryUserMixin()
        view.groups = ["inventory"]
        view.request = Mock(user=self.user)
        self.assertTrue(view.test_func())

    def test_invalid_group(self):
        view = views.InventoryUserMixin()
        view.groups = ["labelmaker"]
        view.request = Mock(user=self.user)
        self.assertFalse(view.test_func())


class TestSKUGeneratorView(InventoryViewTest, ViewTests):
    URL = "/inventory/sku_generator/"
    template = "inventory/sku_generator.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_content(self):
        response = self.make_get_request()
        content = response.content.decode("utf8")
        self.assertIn(reverse("inventory:get_new_sku"), content)
        self.assertIn(reverse("inventory:get_new_range_sku"), content)


class TestCreateBayView(InventoryViewTest, ViewTests):
    fixtures = ("inventory/location",)

    URL = "/inventory/create_warehouse_bay/"
    template = "inventory/create_warehouse_bay.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    @patch("inventory.models.locations.CCAPI")
    def test_post_method(self, mock_CCAPI):
        bay_ID = "846156"
        mock_CCAPI.add_bay_to_warehouse.return_value = bay_ID
        warehouse = models.Warehouse.objects.get(id=1)
        name = "New Bay"
        bay_type = "primary"
        data = {
            "name": name,
            "department": warehouse.warehouse_ID,
            "bay_type": bay_type,
        }
        response = self.client.post(self.URL, data)
        self.assertRedirects(response, self.URL)
        assert (
            models.Bay.objects.filter(
                bay_ID=bay_ID, name=name, warehouse=warehouse
            ).exists()
            is True
        )

    @patch("inventory.models.locations.CCAPI")
    def test_post_create_backup_bay(self, mock_CCAPI):
        bay_ID = "846156"
        mock_CCAPI.add_bay_to_warehouse.return_value = bay_ID
        warehouse = models.Warehouse.objects.get(id=1)
        location = models.Warehouse.objects.get(id=2)
        name = "New Bay"
        bay_type = "backup"
        data = {
            "name": name,
            "department": warehouse.warehouse_ID,
            "bay_type": bay_type,
            "location": location.warehouse_ID,
        }
        response = self.client.post(self.URL, data)
        self.assertRedirects(response, self.URL)
        expected_name = f"{warehouse.abriviation} Backup {location.name} {name}"
        self.assertTrue(
            models.Bay.objects.filter(
                bay_ID=bay_ID, name=expected_name, warehouse=warehouse
            ).exists()
        )

    @patch("inventory.models.locations.CCAPI")
    def test_post_create_backup_bay_without_location(self, mock_CCAPI):
        bay_ID = "846156"
        mock_CCAPI.get_bay_id.return_value = bay_ID
        warehouse = models.Warehouse.objects.get(id=1)
        name = "New Bay"
        bay_type = "backup"
        data = {
            "name": name,
            "department": warehouse.warehouse_ID,
            "bay_type": bay_type,
        }
        response = self.client.post(self.URL, data)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn(
            "Location is required for backup bays.",
            str(response.context["form"].errors),
        )
