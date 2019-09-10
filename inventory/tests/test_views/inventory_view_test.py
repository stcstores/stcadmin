from home.tests.test_views.view_test import ViewTest


class InventoryViewTest(ViewTest):
    def setUp(self):
        super().setUp()
        self.add_group("inventory")
