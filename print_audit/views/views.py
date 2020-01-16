"""Miscellaneous views for print audit app."""

from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic.base import TemplateView

from home.models import CloudCommerceUser
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


class PackCountMonitor(TemplateView):
    """View for pack count display."""

    template_name = "print_audit/pack_count_monitor.html"

    def get_context_data(self, *args, **kwargs):
        """Return HttpResponse with pack count data."""
        context = super().get_context_data(*args, **kwargs)
        date = timezone.now()
        qs = (
            CloudCommerceUser.unhidden.annotate(
                pack_count=Count(
                    "cloudcommerceorder",
                    filter=Q(
                        cloudcommerceorder__date_created__year=date.year,
                        cloudcommerceorder__date_created__month=date.month,
                        cloudcommerceorder__date_created__day=date.day,
                    ),
                )
            )
            .filter(pack_count__gt=0)
            .order_by("-pack_count")
        )
        pack_count = [[_.full_name(), _.pack_count] for _ in qs]
        context["pack_counts"] = pack_count
        return context
