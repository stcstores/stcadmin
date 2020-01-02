from django.shortcuts import reverse

from feedback.models import Feedback
from home.models import CloudCommerceUser
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class UserViewTest(STCAdminTest):
    def setUp(self):
        self.create_user()
        self.login_user()

    def remove_group(self):
        pass

    def test_user_not_in_group_get(self):
        pass

    def test_user_not_in_group_post(self):
        pass


class TestUserView(UserViewTest, ViewTests):
    URL = "/user/"
    template = "user/user.html"

    fixtures = (
        "home/cloud_commerce_user",
        "feedback/feedback",
        "feedback/user_feedback",
    )

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("feedback_count", response.context)
        self.assertIsInstance(response.context["feedback_count"], dict)

    def test_feedback_count_without_cloud_commerce_user(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("feedback_count", response.context)
        self.assertIsInstance(response.context["feedback_count"], dict)
        self.assertEqual({}, response.context["feedback_count"])

    def test_feedback_count_witho_cloud_commerce_user(self):
        cc_user = CloudCommerceUser.objects.get(id=1)
        cc_user.stcadmin_user = self.user
        cc_user.save()
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("feedback_count", response.context)
        self.assertIsInstance(response.context["feedback_count"], dict)
        for feedback_type in Feedback.objects.all():
            self.assertIn(feedback_type, response.context["feedback_count"])
            self.assertIsInstance(
                response.context["feedback_count"][feedback_type], int
            )


class TestChangePasswordView(UserViewTest, ViewTests):
    URL = "/user/change_password/"
    template = "user/change_password.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_post_method(self):
        new_password = "THX1152"
        form_data = {
            "old_password": self.USER_PASSWORD,
            "new_password1": new_password,
            "new_password2": new_password,
        }
        response = self.client.post(self.URL, form_data)
        self.assertRedirects(
            response, "/password_change_done/", fetch_redirect_response=False
        )
        self.client.logout()
        self.client.login(username=self.user.username, password=new_password)
        self.assertTrue(self.user.is_authenticated)


class TestChangePasswordDoneView(UserViewTest, ViewTests):
    URL = "/user/change_password_done/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertRedirects(response, reverse("home:login_user"))

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(response, reverse("home:login_user"))
