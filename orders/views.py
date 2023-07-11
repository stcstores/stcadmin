"""Views for the Orders app."""
from datetime import timedelta

from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView

from home.models import Staff
from home.views import UserInGroupMixin
from orders import forms, models


class OrdersUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the orders group."""

    groups = ["orders"]


class Index(OrdersUserMixin, TemplateView):
    """Main view for the orders app."""

    template_name = "orders/index.html"


class PackCountMonitor(TemplateView):
    """View for pack count display."""

    template_name = "orders/pack_count_monitor.html"

    def get_context_data(self, *args, **kwargs):
        """Return HttpResponse with pack count data."""
        context = super().get_context_data(*args, **kwargs)
        date = timezone.now()
        qs = (
            Staff.unhidden.annotate(
                pack_count=Count(
                    "packed_orders",
                    filter=Q(
                        packed_orders__dispatched_at__year=date.year,
                        packed_orders__dispatched_at__month=date.month,
                        packed_orders__dispatched_at__day=date.day,
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


class UndispatchedOrdersData(TemplateView):
    """Return a list of undispatched order counts."""

    template_name = "orders/undispatched_data.html"

    def urgent_orders(self):
        """Return a list of order IDs for urgent undispatched orders."""
        return sorted(
            list(models.Order.objects.urgent().values_list("order_id", flat=True))
        )

    def priority_orders(self, urgent_orders):
        """Return a list of order IDs for undispatched priority orders."""
        priority_orders = (
            models.Order.objects.undispatched()
            .priority()
            .values_list("order_id", flat=True)
        )
        return sorted(list(set(priority_orders) - set(urgent_orders)))

    def non_priority_orders(self, urgent_orders, priority_orders):
        """Return a list of order IDs for orders that are not urgent or priority."""
        undispatched_orders = (
            models.Order.objects.undispatched()
            .filter(recieved_at__gte=timezone.now() - timedelta(days=7))
            .values_list("order_id", flat=True)
        )
        return sorted(
            list(set(undispatched_orders) - set(urgent_orders) - set(priority_orders))
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


class UndispatchedOrders(OrdersUserMixin, TemplateView):
    """Display a count of undispatched orders."""

    template_name = "orders/undispatched.html"


class OrderList(OrdersUserMixin, ListView):
    """Display a filterable list of orders."""

    template_name = "orders/order_list.html"
    model = models.Order
    paginate_by = 50
    orphans = 3
    form_class = forms.OrderListFilter

    def get(self, *args, **kwargs):
        """Instanciate the form."""
        self.form = self.form_class(self.request.GET)
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Return a queryset of orders based on GET data."""
        if self.form.is_valid():
            return self.form.get_queryset()
        return []

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = self.form
        context["page_range"] = self.get_page_range(context["paginator"])
        return context

    def get_page_range(self, paginator):
        """Return a list of pages to link to."""
        if paginator.num_pages < 11:
            return list(range(1, paginator.num_pages + 1))
        else:
            return list(range(1, 11)) + [paginator.num_pages]


@method_decorator(csrf_exempt, name="dispatch")
class ExportOrders(OrdersUserMixin, View):
    """Create a .csv export of order data."""

    form_class = forms.OrderListFilter

    def post(self, *args, **kwargs):
        """Return an HttpResponse contaning the export or a 404 status."""
        form = self.form_class(self.request.POST)
        if form.is_valid():
            orders = form.get_queryset()
            order_ids = list(orders.values_list("id", flat=True))
            models.OrderExportDownload.objects.create_download(
                user_id=self.request.user.id, order_ids=order_ids
            )
            return HttpResponse("ok")
        return HttpResponseNotFound()


@method_decorator(csrf_exempt, name="dispatch")
class OrderExportStatus(OrdersUserMixin, TemplateView):
    """Get the status of the most recent order export."""

    template_name = "orders/order_export_status.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        try:
            context["export_record"] = models.OrderExportDownload.objects.filter(
                user=self.request.user
            ).latest()
        except models.OrderExportDownload.DoesNotExist:
            context["export_record"] = None
        else:
            context["order_count"] = len(context["export_record"].order_ids)
        return context


class OrderProfit(OrdersUserMixin, TemplateView):
    """View for details of individual orders."""

    template_name = "orders/order_profit.html"

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        order_id = self.kwargs.get("order_id")
        context["order"] = get_object_or_404(models.Order, id=order_id)
        context["products"] = context["order"].productsale_set.all()
        return context
