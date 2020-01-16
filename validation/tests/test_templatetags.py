from unittest.mock import Mock

from stcadmin.tests.stcadmin_test import STCAdminTest
from validation.levels import Levels
from validation.templatetags import validation_extras


class TestValidationTableGroup(STCAdminTest):
    def test_validation_table_group(self):
        group_name = "Group"
        stats = {"levels": {Levels.CRITICAL: 3}, "total": 3}
        errors = [Mock(error_message="Error", level=Levels.CRITICAL)]
        group_name_url = "/validation/group"
        content = validation_extras.validation_table_group(
            group_name, stats, errors, group_name_url=group_name_url
        )
        self.assertIn(group_name, content)
        self.assertIn(Levels.CRITICAL.name, content)
        self.assertIn(Levels.CRITICAL.html_class, content)
        self.assertIn(str(stats["total"]), content)
        self.assertIn(errors[0].error_message, content)
        self.assertIn(group_name_url, content)

    def test_error_level_filter(self):
        content = validation_extras.error_level_filter()
        for level in Levels.all():
            self.assertIn(level.name, content)
