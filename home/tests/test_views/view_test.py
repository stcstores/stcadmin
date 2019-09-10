from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class ViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username="testuser", email="tester@test.com", password="12345"
        )
        login = self.client.login(username="testuser", password="12345")
        self.assertTrue(login)

    def add_group(self, group_name):
        Group.objects.get(name="inventory").user_set.add(self.user)
