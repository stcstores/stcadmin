from datetime import datetime, timedelta
from unittest.mock import patch

from django.utils import timezone

from feedback import forms
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestFeedbackDateFilterForm(STCAdminTest):
    form_class = forms.FeedbackDateFilterForm
    mock_time = timezone.make_aware(datetime(2019, 5, 4))

    def test_default_dates(self):
        form = self.form_class({})
        self.assertEqual({form.DATES: form.ALL}, form.data)

    def test_is_valid(self):
        form = self.form_class({})
        self.assertTrue(form.is_valid())

    @patch("feedback.forms.timezone.now")
    def test_all(self, mock_now):
        mock_now.return_value = self.mock_time
        date_from, date_to = self.form_class().get_date_range(
            {self.form_class.DATES: self.form_class.ALL}
        )
        self.assertEqual(date_from, timezone.make_aware(datetime(1970, 1, 1)))
        self.assertEqual(date_to, timezone.make_aware(datetime(2020, 5, 3)))

    @patch("feedback.forms.timezone.now")
    def test_today(self, mock_now):
        mock_now.return_value = self.mock_time
        date_from, date_to = self.form_class().get_date_range(
            {self.form_class.DATES: self.form_class.TODAY}
        )
        self.assertEqual(date_from, self.mock_time)
        self.assertEqual(date_to, self.mock_time + timedelta(days=1))

    @patch("feedback.forms.timezone.now")
    def test_yesterday(self, mock_now):
        mock_now.return_value = self.mock_time
        date_from, date_to = self.form_class().get_date_range(
            {self.form_class.DATES: self.form_class.YESTERDAY}
        )
        self.assertEqual(date_from, self.mock_time - timedelta(days=1))
        self.assertEqual(date_to, self.mock_time)

    @patch("feedback.forms.timezone.now")
    def test_this_week(self, mock_now):
        mock_now.return_value = self.mock_time
        date_from, date_to = self.form_class().get_date_range(
            {self.form_class.DATES: self.form_class.THIS_WEEK}
        )
        self.assertEqual(
            date_from, self.mock_time - timedelta(days=self.mock_time.weekday())
        )
        self.assertEqual(
            date_to,
            self.mock_time
            - timedelta(days=self.mock_time.weekday())
            + timedelta(days=7),
        )

    @patch("feedback.forms.timezone.now")
    def test_this_month(self, mock_now):
        mock_now.return_value = self.mock_time
        date_from, date_to = self.form_class().get_date_range(
            {self.form_class.DATES: self.form_class.THIS_MONTH}
        )
        self.assertEqual(date_from, timezone.make_aware(datetime(2019, 5, 1)))
        self.assertEqual(date_to, timezone.make_aware(datetime(2019, 6, 1)))

    @patch("feedback.forms.timezone.now")
    def test_last_month(self, mock_now):
        mock_now.return_value = self.mock_time
        date_from, date_to = self.form_class().get_date_range(
            {self.form_class.DATES: self.form_class.LAST_MONTH}
        )
        self.assertEqual(date_from, timezone.make_aware(datetime(2019, 4, 1)))
        self.assertEqual(date_to, timezone.make_aware(datetime(2019, 5, 1)))

    @patch("feedback.forms.timezone.now")
    def test_last_month_january(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime(2019, 1, 12))
        date_from, date_to = self.form_class().get_date_range(
            {self.form_class.DATES: self.form_class.LAST_MONTH}
        )
        self.assertEqual(date_from, timezone.make_aware(datetime(2018, 12, 1)))
        self.assertEqual(date_to, timezone.make_aware(datetime(2019, 1, 1)))

    @patch("feedback.forms.timezone.now")
    def test_this_year(self, mock_now):
        mock_now.return_value = self.mock_time
        date_from, date_to = self.form_class().get_date_range(
            {self.form_class.DATES: self.form_class.THIS_YEAR}
        )
        self.assertEqual(date_from, timezone.make_aware(datetime(2019, 1, 1)))
        self.assertEqual(date_to, timezone.make_aware(datetime(2020, 1, 1)))

    def test_custom(self):
        expected_date_from = timezone.make_aware(datetime(2018, 5, 4))
        expected_date_to = timezone.make_aware(datetime(2019, 8, 17))
        date_from, date_to = self.form_class().get_date_range(
            {
                self.form_class.DATES: self.form_class.CUSTOM,
                self.form_class.DATE_FROM: expected_date_from,
                self.form_class.DATE_TO: expected_date_to,
            }
        )
        self.assertEqual(date_from, expected_date_from)
        self.assertEqual(date_to, expected_date_to)

    def test_invalid_dates(self):
        with self.assertRaises(Exception):
            self.form_class().get_date_range({self.form_class.DATES: "invalid_input"})
