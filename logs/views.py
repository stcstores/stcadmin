"""View for logs."""

import datetime as dt

from django.urls import reverse
from django.utils import timezone
from django.views.generic import RedirectView, TemplateView
from django.views.generic.edit import FormView

from fba.models import FBAOrder
from home.models import Staff
from home.views import UserInGroupMixin
from logs import forms, models


class LogsUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the logs group."""

    groups = ["logs"]


class Index(LogsUserMixin, TemplateView):
    """Index view for the Logs app."""

    template_name = "logs/index.html"


class FBALogDate(LogsUserMixin, RedirectView):
    """Redirect to the FBA log page for a given date or today."""

    def get_date_from_params(self):
        """Return passed date."""
        form = forms.FBALogsDateSelect(self.request.GET)
        if form.is_valid() and form.cleaned_data["date"]:
            return form.cleaned_data["date"]

    def get_redirect_url(self, *args, **kwargs):
        """Return URL to redirect to."""
        date = self.get_date_from_params() or timezone.now().date()
        return reverse(
            "logs:fba_logs",
            kwargs={"year": date.year, "month": date.month, "day": date.day},
        )


class FBALog(LogsUserMixin, TemplateView):
    """FBA log view."""

    template_name = "logs/fba_logs.html"

    def get_date(self):
        """Return the selected date."""
        return dt.date(
            year=self.kwargs["year"], month=self.kwargs["month"], day=self.kwargs["day"]
        )

    def get_fba_orders(self, staff_member, date):
        """Return all FBA orders packed by staff member on date."""
        orders = FBAOrder.objects.filter(
            fulfilled_by=staff_member, closed_at__date=date
        )
        return orders

    def get_work_logs(self, staff_member, date):
        """Return work logs for staff_member on date."""
        return models.WorkLog.objects.filter(staff_member=staff_member, date=date)

    def get_day_url(self, date):
        """Return the URL for the FBA logs for a given date."""
        return reverse(
            "logs:fba_logs",
            kwargs={"year": date.year, "month": date.month, "day": date.day},
        )

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = forms.FBALogsDateSelect(self.request.GET)
        date = self.get_date()
        context["date"] = date
        context["today_url"] = self.get_day_url(timezone.now().date())
        context["yesterday_url"] = self.get_day_url(date - dt.timedelta(days=1))
        context["tomorrow_url"] = self.get_day_url(date + dt.timedelta(days=1))
        staff = Staff.objects.filter(is_on_fba_log__isnull=False, hidden=False)
        for staff_member in staff:
            staff_member.orders = self.get_fba_orders(staff_member, date)
            staff_member.jobs = self.get_work_logs(staff_member, date)
        context["staff"] = staff
        return context


class UpdateWorkLog(FormView):
    """View for manageing work logs."""

    form_class = forms.WorkLogFormset
    template_name = "logs/update_work_log.html"

    def get_form_kwargs(self):
        """Return form kwargs."""
        kwargs = super().get_form_kwargs()
        date = self.get_date()
        staff_member = self.get_staff_member()
        kwargs["queryset"] = models.WorkLog.objects.filter(
            staff_member=staff_member, date=date
        )
        kwargs["initial"] = [{"staff_member": staff_member, "date": date}] * 5
        return kwargs

    def get_date(self):
        """Return the selected date."""
        return dt.date(
            year=self.kwargs["year"], month=self.kwargs["month"], day=self.kwargs["day"]
        )

    def get_staff_member(self):
        """Return the logged in member of staff."""
        return self.request.user.staff_member

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["date"] = self.get_date()
        context["staff_member"] = self.get_staff_member()
        context["formset"] = context.pop("form")
        return context

    def form_valid(self, formset):
        """Save form."""
        if formset.is_valid():
            formset.save()
        else:
            print(formset.errors)
        return super().form_valid(formset)

    def get_success_url(self):
        """Return the success URL."""
        date = self.get_date()
        return reverse(
            "logs:fba_logs",
            kwargs={"year": date.year, "month": date.month, "day": date.day},
        )
