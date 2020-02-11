from datetime import datetime, timedelta
from unittest.mock import Mock

import humanize

from spring_manifest.templatetags import manifest_extras
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestGetUpdateAge(STCAdminTest):
    def test_recent(self):
        update = Mock()
        update.time_since_update.return_value = timedelta(minutes=4)
        self.assertEqual("recent", manifest_extras.get_update_age(update))

    def test_not_recent(self):
        update = Mock()
        update.time_since_update.return_value = timedelta(minutes=9)
        self.assertEqual("not_recent", manifest_extras.get_update_age(update))

    def test_old(self):
        update = Mock()
        update.time_since_update.return_value = timedelta(minutes=11)
        self.assertEqual("old", manifest_extras.get_update_age(update))

    def test_get_update_age_error(self):
        update = Mock(finished=None)
        self.assertEqual("failed", manifest_extras.get_update_age(update))


class TestHumanizeTime(STCAdminTest):
    def test_humanize_time(self):
        time = datetime(2020, 2, 4)
        self.assertEqual(
            manifest_extras.humanize_time(time), humanize.naturaltime(time)
        )
