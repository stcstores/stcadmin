"""Test app groups are created in database."""

from django.contrib.auth.models import Group

from stcadmin.tests.stcadmin_test import STCAdminTest


class TestAppGroupsCreated(STCAdminTest):
    """Test app groups are created in database."""

    def test_app_groups_exist(self):
        """Test app groups are created in database."""
        group_names = [group.name for group in Group.objects.all()]
        self.assertIn("labelmaker", group_names)
