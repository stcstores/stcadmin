from unittest.mock import Mock

from django.contrib.auth.models import Group
from django.db.models.query import QuerySet
from django.utils.safestring import SafeString

from home.templatetags import stcadmin_extras
from stcadmin import settings
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestTooltipTag(STCAdminTest):
    def test_tooltip_tag(self):
        title = "Tooltip Title"
        text = "The Text for a tootlip"
        returned_value = stcadmin_extras.tooltip(title=title, text=text)
        self.assertIsInstance(returned_value, SafeString)
        self.assertIn('class="tooltip', returned_value)
        self.assertIn(f'tooltiptitle="{title}"', returned_value)
        self.assertIn(f'tooltiptext="{text}"', returned_value)


class TestuserGroupsTag(STCAdminTest):
    def setUp(self):
        self.create_user()

    def test_user_groups(self):
        Group.objects.get(name="inventory").user_set.add(self.user)
        Group.objects.get(name="labelmaker").user_set.add(self.user)
        queryset = stcadmin_extras.user_groups(self.user)
        self.assertIsInstance(queryset, QuerySet)
        groups = list(queryset)
        self.assertCountEqual(["inventory", "labelmaker"], groups)

    def test_user_groups_with_no_groups(self):
        queryset = stcadmin_extras.user_groups(self.user)
        self.assertIsInstance(queryset, QuerySet)
        groups = list(queryset)
        self.assertEqual([], groups)


class TestTooltipHelpTextTag(STCAdminTest):
    def test_tooltip_help_text(self):
        text = "A Description of the field."
        label = "Field Name"
        field = Mock(help_text=text, label=label)
        returned_value = stcadmin_extras.tooltip_help_text(field)
        self.assertIsInstance(returned_value, SafeString)
        self.assertIn('class="tooltip', returned_value)
        self.assertIn(f'tooltiptitle="{label}"', returned_value)
        self.assertIn(f'tooltiptext="{text}"', returned_value)

    def test_None_argument(self):
        returned_value = stcadmin_extras.tooltip_help_text(None)
        self.assertEqual("", returned_value)

    def test_empty_help_text(self):
        label = "Field Name"
        field = Mock(help_text="", label=label)
        returned_value = stcadmin_extras.tooltip_help_text(field)
        self.assertEqual("", returned_value)


class TestScaytCustomerID(STCAdminTest):
    def test_scayt_customer_ID(self):
        self.assertEqual(
            settings.SCAYT_CUSTOMER_ID, stcadmin_extras.scayt_customer_id()
        )
