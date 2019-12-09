from home import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestCloudCommerceUser(STCAdminTest):
    fixtures = ("home/cloud_commerce_user",)

    def test_create_object(self):
        self.create_user()
        user_ID = "8493849"
        stcadmin_user = self.user
        first_name = "Test"
        second_name = "User"
        user = models.CloudCommerceUser.objects.create(
            user_id=user_ID,
            stcadmin_user=stcadmin_user,
            first_name=first_name,
            second_name=second_name,
        )
        self.assertTrue(
            models.CloudCommerceUser.objects.filter(user_id=user_ID).exists()
        )
        self.assertEqual(user_ID, user.user_id)
        self.assertEqual(stcadmin_user, user.stcadmin_user)
        self.assertEqual(first_name, user.first_name)
        self.assertEqual(second_name, user.second_name)
        self.assertFalse(user.hidden)

    def test_full_name(self):
        user = models.CloudCommerceUser.objects.get(id=1)
        self.assertEqual("Test", user.first_name)
        self.assertEqual("User", user.second_name)
        self.assertEqual("Test User", user.full_name())

    def test_str_(self):
        user = models.CloudCommerceUser.objects.get(id=1)
        self.assertEqual("Test", user.first_name)
        self.assertEqual("User", user.second_name)
        self.assertEqual("Test User", str(user))

    def test_unhidden_manager(self):
        self.assertTrue(models.CloudCommerceUser.objects.filter(hidden=True).exists())
        unhidden_users = models.CloudCommerceUser.unhidden.all()
        self.assertEqual(3, unhidden_users.count())
        for user in unhidden_users:
            self.assertFalse(user.hidden)
