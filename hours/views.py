"""Views for the Hours app."""

import datetime as dt
import itertools
from calendar import Calendar

from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView, RedirectView, TemplateView

from home.views import UserLoginMixin
from hours import forms, models


class UserCanClockInMixin(UserLoginMixin, UserPassesTestMixin):
    """View mixin to ensure user is logged in and in a given group."""

    def test_func(self):
        """Test user is in a group."""
        return self.request.user.staff_member.can_clock_in


class Hours(UserCanClockInMixin, TemplateView):
    """Manage hours."""

    template_name = "hours/index.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        now = timezone.now()
        start_date = dt.date(now.year, (now.month - 2) % 12, 1)
        times = models.ClockTime.objects.filter(
            user=self.request.user.staff_member, timestamp__date__gte=start_date
        )
        context["latest_time"] = times.last()
        context["times"] = self.make_calendar()
        return context

    def make_calendar(self):
        """Return a dict of clock times."""
        calendar = Calendar()
        now = timezone.now()
        days = {}
        for i in range(3):
            month = dt.date(now.year, (now.month - i) % 12, 1)
            days[month] = {}
            for day in (
                _
                for _ in calendar.itermonthdates(month.year, month.month)
                if _.month == month.month and _ <= now.date()
            ):
                days[month][day] = list(
                    itertools.batched(
                        models.ClockTime.objects.filter(
                            user=self.request.user.staff_member, timestamp__date=day
                        ),
                        2,
                    )
                )
        return days


class Clock(UserCanClockInMixin, RedirectView):
    """Add a clock time."""

    def get_redirect_url(self):
        """Add a clock time."""
        try:
            models.ClockTime.objects.clock(self.request.user.staff_member)
        except models.ClockTime.objects.ClockedTooSoonError:
            return reverse("hours:clocked_too_soon")
        return reverse("hours:hours")


class ClockedTooSoon(UserCanClockInMixin, TemplateView):
    """Error page when a user clocks twice in the same minute."""

    template_name = "hours/clocked_too_soon.html"


class UpdateHours(UserCanClockInMixin, FormView):
    """Form for updating hours for a day."""

    template_name = "hours/update_hours.html"
    form_class = forms.ClockFormSet

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["formset"] = context.pop("form")
        return context

    def get_date(self):
        """Return the date to be edited."""
        return timezone.make_aware(
            dt.datetime.strptime(self.kwargs["date"], "%Y%m%d")
        ).date()

    def get_form_kwargs(self):
        """Return form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["date"] = self.get_date()
        kwargs["user"] = self.request.user.staff_member
        return kwargs

    def post(self, request, *args, **kwargs):
        """Process the formset."""
        formset = self.get_form()
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        """Save form."""
        formset.save()
        return super().form_valid(formset)

    def form_invalid(self, formset):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_success_url(self):
        """Return redrect URL."""
        return reverse("hours:hours")
