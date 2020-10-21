from unittest.mock import Mock

from django.contrib.auth.models import Group
from django.shortcuts import reverse

from inventory import views
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
