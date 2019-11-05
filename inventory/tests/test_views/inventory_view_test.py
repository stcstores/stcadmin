from stcadmin.tests.stcadmin_test import STCAdminTest


class InventoryViewTest(STCAdminTest):
    group_name = "inventory"

    @classmethod
    def setUpTestData(cls):
        cls.create_user()

    def setUp(self):
        super().setUp()
        self.user = self.__class__.user
        self.add_group("inventory")
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)
