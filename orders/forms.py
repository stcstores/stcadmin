"""Forms for print audit app."""
import calendar
import datetime as dt

from django import forms
from django.db.models import Count, Q
from django.utils import timezone

from home.models import Staff
from orders import models
from shipping.models import Country


class ChartSettingsForm(forms.Form):
    """Form for setting options for Charts."""

    number_of_weeks = forms.IntegerField(
        min_value=10, max_value=250, widget=forms.NumberInput(attrs={"step": "10"})
    )


class OrderListFilter(forms.Form):
    """Form for filtering the shipping method list."""

    DISPATCHED = "dispatched"
    UNDISPATCHED = "undispatched"
    ANY = "any"
    SHOW = "show"
    HIDE = "hide"

    order_id = forms.CharField(required=False)
    country = forms.ModelChoiceField(
        Country.objects.all().order_by("name"), required=False
    )
    channel = forms.ModelChoiceField(
        models.Channel.objects.all().order_by("name"), required=False
    )
    recieved_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    recieved_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    status = forms.ChoiceField(
        choices=(
            (ANY, "Any"),
            (DISPATCHED, "Dispatched"),
            (UNDISPATCHED, "Undispatched"),
        ),
        required=False,
    )

    def clean_recieved_from(self):
        """Return a timezone aware dt object from the submitted date."""
        date = self.cleaned_data["recieved_from"]
        if date is not None:
            return timezone.make_aware(
                dt.datetime.combine(date, dt.datetime.min.time())
            )

    def clean_recieved_to(self):
        """Return a timezone aware dt object from the submitted date."""
        date = self.cleaned_data["recieved_to"]
        if date is not None:
            return timezone.make_aware(
                dt.datetime.combine(date, dt.datetime.max.time())
            )

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "country": data.get("country"),
            "channel": data.get("channel"),
            "recieved_at__gte": data.get("recieved_from"),
            "recieved_at__lte": data.get("recieved_to"),
            "order_id": data.get("order_id") or None,
        }
        return {key: value for key, value in kwargs.items() if value is not None}

    def get_queryset(self):
        """Return a queryset of orders based on the submitted data."""
        kwargs = self.query_kwargs(self.cleaned_data)
        qs = models.Order.objects.filter(**kwargs)
        if self.cleaned_data.get("status") == self.DISPATCHED:
            qs = qs.dispatched()
        elif self.cleaned_data.get("status") == self.UNDISPATCHED:
            qs = qs.undispatched()
        return (
            qs.order_by("-recieved_at")
            .prefetch_related("productsale_set")
            .select_related(
                "shipping_service",
                "channel",
                "country",
                "country__region",
            )
            .distinct()
        )


class PackingMistakeForm(forms.ModelForm):
    """Form for packing mistakes."""

    class Meta:
        """Meta class for Packing Mistake Form."""

        model = models.PackingMistake
        fields = ["user", "timestamp", "order_id", "note"]
        widgets = {"timestamp": forms.DateInput(attrs={"class": "datepicker"})}

    def __init__(self, *args, **kwargs):
        """Set the user queryset."""
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = Staff.unhidden.all()


class PackCountFilter(forms.Form):
    """Form for filtering packing counts."""

    # month = forms.ChoiceField()
    # year = forms.ChoiceField()

    # def __init__(self, *args, **kwargs):
    #     """Set choices."""
    #     super().__init__(*args, **kwargs)
    #     now = timezone.now()
    #     self.fields["month"].choices = (
    #         (i, month) for i, month in enumerate(calendar.month_name[1:], 1)
    #     )
    #     self.fields["year"].choices = (
    #         (year, str(year))
    #         for year in reversed(
    #             sorted(
    #                 models.Order.objects.filter(dispatched_at__isnull=False)
    #                 .values_list("dispatched_at__year", flat=True)
    #                 .distinct()
    #             )
    #         )
    #     )
    #     self.initial = {"year": now.year, "month": now.month}

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
        date_to = date_from + dt.timedelta(days=1)
        return (date_from, date_to)

    def yesterday(self):
        """Return start and end dates for the previous day."""
        date_to = timezone.now().date()
        date_from = date_to - dt.timedelta(days=1)
        return (date_from, date_to)

    def this_week(self):
        """Return start and end dates for the current week."""
        today = timezone.now().date()
        date_from = today - dt.timedelta(days=today.weekday())
        date_to = date_from + dt.timedelta(days=7)
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
        date_from = dt.datetime(year=today.year, month=1, day=1)
        date_to = dt.datetime(year=today.year + 1, month=1, day=1)
        return (date_from, date_to)

    DATE_METHODS = {
        THIS_YEAR: this_year,
        LAST_MONTH: last_month,
        THIS_MONTH: this_month,
        THIS_WEEK: this_week,
        YESTERDAY: yesterday,
        TODAY: today,
    }

    day = dt.timedelta(days=1)

    dates = forms.ChoiceField(choices=DATES_CHOICES, widget=(forms.RadioSelect))

    date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    date_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    def get_month_range(self, year, month):
        """Return first and last day for month."""
        days_in_month = calendar.monthrange(year, month)[1]
        date_from = dt.datetime(year=year, month=month, day=1)
        date_to = date_from + dt.timedelta(days_in_month)
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
                dt.datetime(1970, 1, 1),
                timezone.now() + dt.timedelta(days=365),
            )
        elif dates == self.CUSTOM:
            date_from, date_to = (data[self.DATE_FROM], data[self.DATE_TO])
        elif dates in self.DATE_METHODS:
            date_from, date_to = self.DATE_METHODS[dates](self)
        else:
            raise Exception(f'"dates" value {dates} not recognised.')
        date_from = self.localise_time(date_from)
        date_to = self.localise_time(date_to)
        return sorted((date_from, date_to))

    def localise_time(self, time):
        """Localise datetime object."""
        time = dt.datetime.combine(time, dt.datetime.min.time())
        time = timezone.make_aware(time)
        return time

    def get_queryset(self):
        """Return a queryset of User objects annotated with pack and mistake counts."""
        if self.is_valid():
            date_from, date_to = self.get_date_range(self.cleaned_data)
            qs = Staff.unhidden.order_by("first_name", "second_name").annotate(
                pack_count=Count(
                    "packed_orders",
                    filter=Q(
                        packed_orders__dispatched_at__gte=date_from,
                        packed_orders__dispatched_at__lte=date_to,
                    ),
                    distinct=True,
                ),
                mistake_count=Count(
                    "packing_mistakes",
                    filter=Q(
                        packing_mistakes__timestamp__gte=date_from,
                        packing_mistakes__timestamp__lte=date_to,
                    ),
                    distinct=True,
                ),
            )
            print(date_from, date_to)
            return qs
        raise Exception("Error parsing form.")


class PackingMistakeFilterForm(forms.Form):
    """Form for filtering packing mistakes."""

    user = forms.ChoiceField(required=False)
    made_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    made_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    def __init__(self, *args, **kwargs):
        """Set choices."""
        super().__init__(*args, **kwargs)
        self.fields["user"].choices = [("", "Any")] + [
            (_.id, str(_)) for _ in Staff.unhidden.all()
        ]

    def clean_made_from(self):
        """Return a timezone aware dt object from the submitted date."""
        date = self.cleaned_data["made_from"]
        if date is not None:
            return timezone.make_aware(dt.combine(date, dt.min.time()))

    def clean_made_to(self):
        """Return a timezone aware dt object from the submitted date."""
        date = self.cleaned_data["made_to"]
        if date is not None:
            return timezone.make_aware(dt.combine(date, dt.max.time()))

    def get_queryset(self):
        """Return a queryset with filters."""
        if self.is_valid():
            data = self.cleaned_data
            qs = models.PackingMistake.objects.all()
            if user := data["user"]:
                qs = qs.filter(user=user)
            if made_from := data["made_from"]:
                qs = qs.filter(timestamp__gte=made_from)
            if made_to := data.get("made_to"):
                qs = qs.filter(timestamp__lte=made_to)
            return qs
        raise Exception("Form Invalid")
