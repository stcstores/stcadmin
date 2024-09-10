"""Forms for the Hours app."""

import datetime as dt

from django import forms
from django.db import transaction
from django.utils import timezone

from hours import models


class ClockForm(forms.Form):
    """Form for adding a clock time."""

    hour = forms.IntegerField(
        widget=forms.NumberInput(attrs={"min": 0, "max": 23, "class": "text-end"})
    )
    minute = forms.IntegerField(widget=forms.NumberInput(attrs={"min": 0, "max": 59}))

    def clean(self):
        """Add time to cleaned data."""
        self.cleaned_data = super().clean()
        self.cleaned_data["time"] = dt.time(
            hour=self.cleaned_data["hour"], minute=self.cleaned_data["minute"]
        )
        return self.cleaned_data


class BaseClockFormSet(forms.BaseFormSet):
    """Base class for ClockFormSet."""

    def __init__(self, *args, **kwargs):
        """Initialise formset."""
        self.date = kwargs.pop("date")
        self.user = kwargs.pop("user")
        self.times = models.ClockTime.objects.filter(
            user=self.user, timestamp__date=self.date
        )
        kwargs["initial"] = self.get_initial()
        super().__init__(*args, **kwargs)

    def get_initial(self):
        """Return initial values for the form."""
        return [
            {
                "hour": timezone.make_naive(time.timestamp).hour,
                "minute": timezone.make_naive(time.timestamp).minute,
            }
            for time in self.times
        ]

    def save(self):
        """Update ClockTime mode."""
        with transaction.atomic():
            self.times.delete()
            for form_data in self.cleaned_data:
                if form_data:
                    timestamp = timezone.make_aware(
                        dt.datetime.combine(self.date, form_data["time"])
                    )
                    obj = models.ClockTime(user=self.user, timestamp=timestamp)
                    obj.full_clean()
                    obj.save()


ClockFormSet = forms.formset_factory(ClockForm, formset=BaseClockFormSet, extra=4)
