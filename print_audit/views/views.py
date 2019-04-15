"""Miscellaneous views for print audit app."""

from django.views.generic.base import TemplateView

from home.views import UserInGroupMixin
from print_audit import charts, forms


class PrintAuditUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the print audit group."""

    groups = ["print_audit"]


class Index(PrintAuditUserMixin, TemplateView):
    """View for print_audit hompage."""

    template_name = "print_audit/index.html"


class Charts(PrintAuditUserMixin, TemplateView):
    """View for displaying charts."""

    template_name = "print_audit/charts.html"
    form_class = forms.ChartSettingsForm
    DEFAULT_WEEKS_TO_DISPLAY = 80

    def post(self, *args, **kwargs):
        """Process POST requests in the same way as GET requests."""
        return self.get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = self.form_class(
            self.request.POST or None,
            initial={"number_of_weeks": self.DEFAULT_WEEKS_TO_DISPLAY},
        )
        orders_by_week_number_of_weeks = int(
            self.request.POST.get("number_of_weeks", self.DEFAULT_WEEKS_TO_DISPLAY)
        )
        context["orders_by_week_chart"] = charts.OrdersByWeek(
            number_of_weeks=orders_by_week_number_of_weeks
        )
        context["orders_by_day_chart"] = charts.OrdersByDay()
        return context
