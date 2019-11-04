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
        user, created = get_user_model().objects.get_or_create(
            username=username or cls.USERNAME,
            defaults={"email": email or cls.USER_EMAIL},
        )
        if created:
            user.set_password(password or cls.USER_PASSWORD)
            user.save()
        if username is None:
            cls.user = user
        return user

    @classmethod
    def add_group(cls, group_name):
        Group.objects.get(name=group_name).user_set.add(cls.user)

    def login_user(self):
        user = self.create_user()
        login = self.client.login(username=user.username, password=self.USER_PASSWORD)
        self.assertTrue(login)

    def user_logged_in(self):
        return "_auth_user_id" in self.client.session
