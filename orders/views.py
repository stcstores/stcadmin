"""Views for the Orders app."""
from datetime import timedelta

from django.db.models import Count, Q
from django.shortcuts import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from home.models import CloudCommerceUser
from home.views import UserInGroupMixin
from orders import forms, models


class OrdersUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the print audit group."""

    groups = ["orders"]


class Index(OrdersUserMixin, TemplateView):
    """Main view for the orders app."""

    template_name = "orders/index.html"


class BreakageIndex(OrdersUserMixin, TemplateView):
    """Main view for breakages."""

    template_name = "orders/breakages.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        context["breakages"] = models.Breakage.objects.all()
        return context


class AddBreakage(OrdersUserMixin, CreateView):
    """View for creating new Breakage objects."""

    model = models.Breakage
    fields = ["product_sku", "order_id", "note", "packer"]

    def get_success_url(self):
        """Return URL to redirect to after succesfull form submission."""
        return reverse("orders:breakages")


class UpdateBreakage(OrdersUserMixin, UpdateView):
    """View for updating Breakage objects."""

    model = models.Breakage
    fields = ["product_sku", "order_id", "note", "packer"]

    def get_object(self, queryset=None):
        """Return object to update."""
        return models.Breakage.objects.get(id=self.kwargs["breakage_id"])

    def get_success_url(self):
        """Return URL to redirect to after succesfull form submission."""
        return reverse("orders:breakages")


class DeleteBreakage(OrdersUserMixin, DeleteView):
    """View for deleting Breakage objects."""

    model = models.Breakage

    def get_object(self, queryset=None):
        """Return object to delete."""
        return models.Breakage.objects.get(id=self.kwargs["breakage_id"])

    def get_success_url(self):
        """Return URL to redirect to after succesfull form submission."""
        return reverse("orders:breakages")


class PackCountMonitor(TemplateView):
    """View for pack count display."""

    template_name = "orders/pack_count_monitor.html"

    def get_context_data(self, *args, **kwargs):
        """Return HttpResponse with pack count data."""
        context = super().get_context_data(*args, **kwargs)
        date = timezone.now()
        qs = (
            CloudCommerceUser.unhidden.annotate(
                pack_count=Count(
                    "packingrecord",
                    filter=Q(
                        packingrecord__order__dispatched_at__year=date.year,
                        packingrecord__order__dispatched_at__month=date.month,
                        packingrecord__order__dispatched_at__day=date.day,
                    ),
                )
            )
            .filter(pack_count__gt=0)
            .order_by("-pack_count")
        )
        pack_count = [[_.full_name(), _.pack_count] for _ in qs]
        context["pack_counts"] = pack_count
        return context


class Charts(OrdersUserMixin, TemplateView):
    """View for displaying charts."""

    template_name = "orders/charts.html"
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
        context["orders_by_week_chart"] = models.charts.OrdersByWeek(
            number_of_weeks=orders_by_week_number_of_weeks
        )
        context["orders_by_day_chart"] = models.charts.OrdersByDay()
        return context


class UndispatchedOrders(OrdersUserMixin, TemplateView):
    """Display a count of undispatched orders."""

    template_name = "orders/undispatched.html"

    def urgent_orders(self):
        """Return a list of order IDs for urgent undispatched orders."""
        return list(models.Order.urgent.values_list("order_ID", flat=True))

    def priority_orders(self, urgent_orders):
        """Return a list of order IDs for undispatched priority orders."""
        priority_orders = models.Order.undispatched_priority.values_list(
            "order_ID", flat=True
        )
        return list(set(priority_orders) - set(urgent_orders))

    def non_priority_orders(self, urgent_orders, priority_orders):
        """Return a list of order IDs for orders that are not urgent or priority."""
        undispatched_orders = models.Order.undispatched.filter(
            recieved_at__gte=timezone.now() - timedelta(days=7)
        ).values_list("order_ID", flat=True)
        return list(
            set(undispatched_orders) - set(urgent_orders) - set(priority_orders)
        )

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        urgent = self.urgent_orders()
        priority = self.priority_orders(urgent)
        non_priority = self.non_priority_orders(urgent, priority)
        context["total"] = len(urgent) + len(priority) + len(non_priority)
        context["priority"] = priority
        context["non_priority"] = non_priority
        context["urgent"] = urgent
        return context
