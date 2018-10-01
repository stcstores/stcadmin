"""Miscellaneous views for print audit app."""

from django.views.generic.base import TemplateView
from home.views import UserInGroupMixin
from print_audit import charts


class PrintAuditUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the print audit group."""

    groups = ["print_audit"]


class Index(PrintAuditUserMixin, TemplateView):
    """View for print_audit hompage."""

    template_name = "print_audit/index.html"


class Charts(PrintAuditUserMixin, TemplateView):
    """View for displaying charts."""

    template_name = "print_audit/charts.html"

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        context["orders_by_week_chart"] = charts.OrdersByWeek()
        context["orders_by_day_chart"] = charts.OrdersByDay()
        return context
