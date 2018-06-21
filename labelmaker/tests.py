"""Tests for labelmaker app."""

from django.contrib.auth.models import Group, User
from django.test import TestCase


class LabelMakerTemplateTest(TestCase):
    """Tests for labelmaker templates."""

    GROUP = 'labelmaker'

    def setUp(self):
        """Login user."""
        user = User.objects.create_user('foo', 'myemail@test.com', 'bar')
        self.client.login(username='foo', password='bar')
        group = Group.objects.get(name=self.GROUP)
        group.user_set.add(user)

    def template_test(self, url, template):
        """Test url uses template."""
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

    def test_uses_index_template(self):
        """Test labelmaker index page uses the correct template."""
        self.template_test('/labelmaker/', 'labelmaker/index.html')
