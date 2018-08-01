"""Test app groups are created in database."""

from django.contrib.auth.models import Group
from django.test import TestCase


class TestAppGroupsCreated(TestCase):
    """Test app groups are created in database."""

    def test_app_groups_exist(self):
        """Test app groups are created in database."""
        group_names = [group.name for group in Group.objects.all()]
        self.assertIn("labelmaker", group_names)
