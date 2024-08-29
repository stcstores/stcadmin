"""Views for the Hours app."""

import datetime as dt
import itertools
from calendar import Calendar

from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import RedirectView, TemplateView

from home.views import UserLoginMixin
from hours import models


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
