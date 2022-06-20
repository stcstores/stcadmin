"""Forms for the Feedback app."""
import calendar
import datetime

import pytz
from django import forms
from django.conf import settings
from django.utils import timezone

from feedback import models
from home.models import Staff


class FeedbackSearchForm(forms.Form):
    """Form for searching feedback."""

    PAGINATION_VALUES = [5, 10, 25, 50, 100, 250, 500, 1000, 5000]

    PAGINATION_CHOICES = [(None, "")] + [
        (int(num), str(num)) for num in PAGINATION_VALUES
    ]

    user = forms.ModelChoiceField(
        label="User",
        required=False,
        queryset=Staff.objects.all(),
        widget=forms.RadioSelect(),
    )

    feedback = forms.ModelChoiceField(
        label="Feedback Type",
        required=False,
        queryset=models.Feedback.objects.all(),
        widget=forms.RadioSelect(),
    )

    date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    date_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    paginate_by = forms.ChoiceField(choices=PAGINATION_CHOICES)


class FeedbackDateFilterForm(forms.Form):
    """Form for filtering user feedback by date."""

    DATES = "dates"
    DATE_FROM = "date_from"
    DATE_TO = "date_to"
    ALL = "all"
    THIS_YEAR = "this_year"
    LAST_MONTH = "last_month"
    THIS_MONTH = "this_month"
    THIS_WEEK = "this_week"
    YESTERDAY = "yesterday"
    TODAY = "today"
    CUSTOM = "custom"

    DATES_CHOICES = [
        (ALL, "All"),
        (THIS_YEAR, "This Year"),
        (LAST_MONTH, "Last Month"),
        (THIS_MONTH, "This Month"),
        (THIS_WEEK, "This Week"),
        (YESTERDAY, "Yesterday"),
        (TODAY, "Today"),
        (CUSTOM, "Custom"),
    ]

    def __init__(self, *args, **kwargs):
        """Add default dates parameter to data."""
        super().__init__(*args, **kwargs)
        if self.DATES not in self.data:
            self.data[self.DATES] = self.ALL

    def today(self):
        """Return start and end dates for the current day."""
        date_from = timezone.now().date()
        date_to = date_from + datetime.timedelta(days=1)
        return (date_from, date_to)

    def yesterday(self):
        """Return start and end dates for the previous day."""
        date_to = timezone.now().date()
        date_from = date_to - datetime.timedelta(days=1)
        return (date_from, date_to)

    def this_week(self):
        """Return start and end dates for the current week."""
        today = timezone.now().date()
        date_from = today - datetime.timedelta(days=today.weekday())
        date_to = date_from + datetime.timedelta(days=7)
        return (date_from, date_to)

    def this_month(self):
        """Return start and end dates for the current month."""
        now = timezone.now()
        return self.get_month_range(now.year, now.month)

    def last_month(self):
        """Return start and end dates for the previous month."""
        now = timezone.now()
        month = now.month - 1
        year = now.year
        if month == 0:
            month = 12
            year -= 1
        return self.get_month_range(year, month)

    def this_year(self):
        """Return start and end dates for the current year."""
        today = timezone.now()
        date_from = datetime.datetime(year=today.year, month=1, day=1)
        date_to = datetime.datetime(year=today.year + 1, month=1, day=1)
        return (date_from, date_to)

    DATE_METHODS = {
        THIS_YEAR: this_year,
        LAST_MONTH: last_month,
        THIS_MONTH: this_month,
        THIS_WEEK: this_week,
        YESTERDAY: yesterday,
        TODAY: today,
    }

    day = datetime.timedelta(days=1)

    dates = forms.ChoiceField(choices=DATES_CHOICES, widget=(forms.RadioSelect))

    date_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    def get_month_range(self, year, month):
        """Return first and last day for month."""
        days_in_month = calendar.monthrange(year, month)[1]
        date_from = datetime.datetime(year=year, month=month, day=1)
        date_to = date_from + datetime.timedelta(days_in_month)
        return (date_from, date_to)

    def is_valid(self, *args, **kwargs):
        """Validate form and return True."""
        super().is_valid()
        return True

    def clean(self):
        """Set final start and end dates according to submitted data."""
        data = super().clean()
        date_from, date_to = self.get_date_range(data)
        data[self.DATE_FROM] = date_from
        data[self.DATE_TO] = date_to
        return data

    def get_date_range(self, data):
        """Return a sanitized date_from and date_to."""
        dates = data.get(self.DATES)
        if dates == self.ALL:
            date_from, date_to = (
                datetime.datetime(1970, 1, 1),
                timezone.now() + datetime.timedelta(days=365),
            )
        elif dates == self.CUSTOM:
            date_from, date_to = (data[self.DATE_FROM], data[self.DATE_TO])
        elif dates in self.DATE_METHODS:
            date_from, date_to = self.DATE_METHODS[dates](self)
        else:
            raise Exception(f'"dates" value {dates} not recognised.')
        date_from = self.localise_time(date_from)
        date_to = self.localise_time(date_to)
        return date_from, date_to

    def localise_time(self, time):
        """Localise datetime object."""
        tz = pytz.timezone(settings.TIME_ZONE)
        time = datetime.datetime.combine(time, datetime.datetime.min.time())
        time = tz.localize(time)
        return time
