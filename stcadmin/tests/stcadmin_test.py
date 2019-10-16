"""Base test classes."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
@override_settings(CC_DOMAIN="nowhere@nowhere.com")
@override_settings(CC_USERNAME="username")
@override_settings(CC_USERNAME="password")
class STCAdminTest(TestCase):
    """Base class for tests."""

    USERNAME = "testuser"
    USER_EMAIL = "tester@test.com"
    USER_PASSWORD = "AverySECUREpassword"

    @classmethod
    def create_user(cls, username=None, email=None, password=None):
        user = get_user_model().objects.create_user(
            username=username or cls.USERNAME,
            email=email or cls.USER_EMAIL,
            password=password or cls.USER_PASSWORD,
        )
        if username is None:
            cls.user = user
        return user

    @classmethod
    def add_group(cls, group_name):
        Group.objects.get(name=group_name).user_set.add(cls.user)

    def login_user(self):
        login = self.client.login(username=self.USERNAME, password=self.USER_PASSWORD)
        self.assertTrue(login)
