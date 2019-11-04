import sys
from unittest.mock import Mock

from django.shortcuts import reverse

from home import views
from stcadmin import settings
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestUserLoginMixin(STCAdminTest):
    def test_user_login_mixin(self):
        self.assertEqual(settings.LOGIN_URL, views.UserLoginMixin.login_url)


class TestUserInGroupMixin(STCAdminTest):
    def setUp(self):
        self.create_user()
        self.add_group("inventory")
        self.login_user()

    def test_valid_group(self):
        view = views.UserInGroupMixin()
        view.groups = ["inventory"]
        view.request = Mock(user=self.user)
        self.assertTrue(view.test_func())

    def test_invalid_group(self):
        view = views.UserInGroupMixin()
        view.groups = ["labelmaker"]
        view.request = Mock(user=self.user)
        self.assertFalse(view.test_func())


class TestIndexView(STCAdminTest):
    URL = "/"
    template = "home/index.html"

    def setUp(self):
        self.create_user()
        self.add_group("inventory")
        self.login_user()

    def test_get_method(self):
        response = self.client.get(self.URL)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_logged_out_user(self):
        self.client.logout()
        response = self.client.get(self.URL)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.URL}")

    def test_post_method(self):
        response = self.client.post(self.URL)
        self.assertEqual(405, response.status_code)

    def test_template(self):
        response = self.client.get(self.URL)
        self.assertIn("<h1>STC Admin</h1>", str(response.content))
        self.assertIn("Inventory", str(response.content))
        self.assertNotIn("Labelmaker", str(response.content))
        self.assertIn('class="homepage_feedback', str(response.content))


class TestVersionView(STCAdminTest):
    URL = "/version/"
    template = "home/version.html"

    def test_get_method(self):
        response = self.client.get(self.URL)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_post_method(self):
        response = self.client.post(self.URL)
        self.assertEqual(405, response.status_code)

    def test_template(self):
        response = self.client.get(self.URL)
        self.assertIn("django", str(response.content))
        self.assertIn("Python Version", str(response.content))
        self.assertIn("STCAdmin Version", str(response.content))
        self.assertIn("Installed Packages", str(response.content))
        self.assertIn(sys.version.replace("\n", "\\n"), str(response.content))


class TestRobotsView(STCAdminTest):
    URL = "/robots.txt"
    template = "home/robots.txt"

    def test_get_method(self):
        response = self.client.get(self.URL)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_post_method(self):
        response = self.client.post(self.URL)
        self.assertEqual(405, response.status_code)


class TestLoginView(STCAdminTest):
    URL = "/login/"
    template = "home/login.html"

    def setUp(self):
        self.create_user()

    def test_get_method(self):
        self.client.logout()
        response = self.client.get(self.URL)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_post_method(self):
        self.client.logout()
        self.assertFalse(self.user_logged_in())
        response = self.client.post(
            self.URL, {"username": self.USERNAME, "password": self.USER_PASSWORD}
        )
        self.assertTrue(self.user_logged_in())
        self.assertRedirects(response, reverse("home:index"))

    def test_user_already_logged_in(self):
        self.login_user()
        self.assertTrue(self.user_logged_in())
        response = self.client.get(self.URL)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)


class TestLogoutView(STCAdminTest):
    URL = "/logout/"

    def setUp(self):
        self.create_user()

    def test_get_method(self):
        self.login_user()
        response = self.client.get(self.URL)
        self.assertRedirects(response, "/login/")
        self.assertFalse(self.user_logged_in())

    def test_post_method(self):
        self.login_user()
        response = self.client.post(self.URL)
        self.assertRedirects(response, "/login/")
        self.assertFalse(self.user_logged_in())

    def test_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.URL)
        self.assertRedirects(response, "/login/")
        self.assertFalse(self.user_logged_in())
