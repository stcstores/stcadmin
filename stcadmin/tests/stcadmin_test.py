"""Base test classes."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from django.test import TestCase, override_settings

from stcadmin import settings


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

    @classmethod
    def remove_group(cls, group_name):
        Group.objects.get(name=group_name).user_set.remove(cls.user)

    def login_user(self):
        user = self.create_user()
        login = self.client.login(username=user.username, password=self.USER_PASSWORD)
        self.assertTrue(login)

    def user_logged_in(self):
        return "_auth_user_id" in self.client.session


class ViewTests:
    group_name = None
    get_method_status_code = 405
    post_method_status_code = 405

    def get_URL(self):
        return self.URL

    def make_get_request(self):
        return self.client.get(self.get_URL())

    def make_post_request(self):
        return self.client.post(self.get_URL())

    def redirect_URL(self):
        return f"{settings.LOGIN_URL}?next={self.get_URL()}"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(self.get_method_status_code, response.status_code)

    def test_post_method(self):
        response = self.make_post_request()
        self.assertEqual(self.post_method_status_code, response.status_code)

    def test_logged_out_user_get(self):
        self.client.logout()
        response = self.make_get_request()
        self.assertRedirects(response, self.redirect_URL())

    def test_logged_out_user_post(self):
        self.client.logout()
        response = self.make_post_request()
        self.assertRedirects(response, self.redirect_URL())

    def test_user_not_in_group_get(self):
        self.remove_group()
        response = self.make_get_request()
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_user_not_in_group_post(self):
        self.remove_group()
        response = self.make_post_request()
        self.assertIsInstance(response, HttpResponseForbidden)
