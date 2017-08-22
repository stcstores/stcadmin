import datetime
from django.utils import timezone
from django import forms
from print_audit import models
from dateutil.relativedelta import relativedelta
import pytz
from stcadmin import settings


class FeedbackSearchForm(forms.Form):

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

    DATES_CHOICES = [
        ('all', 'All'), ('this_year', 'This Year'),
        ('last_month', 'Last Month'), ('this_month', 'This Month'),
        ('this_week', 'This Week'), ('yesterday', 'Yesterday'),
        ('today', 'Today'), ('custom', 'Custom')]

    dates = forms.ChoiceField(
        choices=DATES_CHOICES, widget=(forms.RadioSelect))

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'datepicker'}))

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'datepicker'}))

    def today(self):
        date_from = timezone.now().date()
        date_to = date_from + datetime.timedelta(days=1)
        return (date_from, date_to)

    def yesterday(self):
        date_to = timezone.now().date()
        date_from = date_to - datetime.timedelta(days=1)
        return (date_from, date_to)

    def this_week(self):
        today = timezone.now().date()
        date_from = today - datetime.timedelta(days=today.weekday())
        date_to = date_from + relativedelta(weeks=1)
        return (date_from, date_to)

    def this_month(self):
        date_from = timezone.now().date().replace(day=1)
        date_to = date_from + relativedelta(months=1)
        return (date_from, date_to)

    def last_month(self):
        date_from = timezone.now().date().replace(
            day=1) - relativedelta(months=2)
        date_to = date_from + relativedelta(months=1)
        return (date_from, date_to)

    def this_year(self):
        today = timezone.now()
        date_from = datetime(year=today.year, month=1, day=1)
        date_to = datetime(year=today.year + 1, month=1, day=1)
        return (date_from, date_to)

    def clean(self):
        data = super().clean()
        if data['dates'] == 'custom':
            data['date_to'] += datetime.timedelta(days=1)
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
        if data['date_from'] is not None:
            data['date_from'] = self.localise_time(data['date_from'])
        if data['date_to'] is not None:
            data['date_to'] = self.localise_time(data['date_to'])
        return data

    def localise_time(self, time):
        tz = pytz.timezone(settings.TIME_ZONE)
        if isinstance(time, datetime.date):
            time = datetime.datetime.combine(
                time, datetime.datetime.min.time())
        time = tz.localize(time)
        return time
