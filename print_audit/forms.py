"""Forms for print audit app."""

import calendar
import datetime

import pytz
from django import forms
from django.utils import timezone

from print_audit import models
from stcadmin import settings


class FeedbackSearchForm(forms.Form):
    """Form for searching feedback."""

    PAGINATION_VALUES = [5, 10, 25, 50, 100, 250, 500, 1000, 5000]

    PAGINATION_CHOICES = [(None, '')] + [
        (int(num), str(num)) for num in PAGINATION_VALUES]

    user = forms.ModelChoiceField(
        label='User',
        required=False,
        queryset=models.CloudCommerceUser.objects.all(),
        widget=forms.RadioSelect())

    feedback = forms.ModelChoiceField(
        label='Feedback Type',
        required=False,
        queryset=models.Feedback.objects.all(),
        widget=forms.RadioSelect())

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'datepicker'}))

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'datepicker'}))

    paginate_by = forms.ChoiceField(
        choices=PAGINATION_CHOICES)


class FeedbackDateFilterForm(forms.Form):
    """Form for filtering user feedback by date."""

    DATES_CHOICES = [
        ('all', 'All'), ('this_year', 'This Year'),
        ('last_month', 'Last Month'), ('this_month', 'This Month'),
        ('this_week', 'This Week'), ('yesterday', 'Yesterday'),
        ('today', 'Today'), ('custom', 'Custom')]

    day = datetime.timedelta(days=1)

    dates = forms.ChoiceField(
        choices=DATES_CHOICES, widget=(forms.RadioSelect))

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'datepicker'}))

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'datepicker'}))

    def get_month_range(self, year, month):
        """Return first and last day for month."""
        last_day = calendar.monthrange(year, month)[1]
        date_from = datetime.datetime(
            year=year, month=month, day=1)
        date_to = datetime.datetime(
            year=year, month=month, day=last_day)
        return (date_from, date_to)

    def today(self):
        """Return start and end dates for the current day."""
        date_from = timezone.now().date()
        date_to = date_from
        return (date_from, date_to)

    def yesterday(self):
        """Return start and end dates for the previous day."""
        date_to = timezone.now().date() - self.day
        date_from = date_to
        return (date_from, date_to)

    def this_week(self):
        """Return start and end dates for the current week."""
        today = timezone.now().date()
        date_from = today - datetime.timedelta(days=today.weekday())
        date_to = date_from + datetime.timedelta(days=6)
        return (date_from, date_to)

    def this_month(self):
        """Return start and end dates for the current month."""
        now = timezone.now()
        return self.get_month_range(now.year, now.month)

    def last_month(self):
        """Return start and end dates for the previous month."""
        now = timezone.now()
        month = now.month - 1
        if month == 0:
            month = 1
        return self.get_month_range(now.year, month)

    def this_year(self):
        """Return start and end dates for the current year."""
        today = timezone.now()
        date_from = datetime.datetime(year=today.year, month=1, day=1)
        date_to = datetime.datetime(year=today.year, month=12, day=31)
        return (date_from, date_to)

    def clean(self):
        """Set final start and end dates according to submitted data."""
        data = super().clean()
        if data['dates'] == 'today':
            data['date_from'], data['date_to'] = self.today()
        if data['dates'] == 'yesterday':
            data['date_from'], data['date_to'] = self.yesterday()
        if data['dates'] == 'this_week':
            data['date_from'], data['date_to'] = self.this_week()
        if data['dates'] == 'this_month':
            data['date_from'], data['date_to'] = self.this_month()
        if data['dates'] == 'last_month':
            data['date_from'], data['date_to'] = self.last_month()
        if data['dates'] == 'this_year':
            data['date_from'], data['date_to'] = self.this_year()
        data['date_from'] = self.clean_time(data['date_from'])
        data['date_to'] = self.clean_time(data['date_to'])
        return data

    def clean_time(self, time):
        """Return cleaned time value in current timezone."""
        if time is None:
            time = timezone.now().date()
        return self.localise_time(time)

    def localise_time(self, time):
        """Localise datetime object."""
        tz = pytz.timezone(settings.TIME_ZONE)
        if isinstance(time, datetime.date):
            time = datetime.datetime.combine(
                time, datetime.datetime.min.time())
        time = tz.localize(time)
        return time
