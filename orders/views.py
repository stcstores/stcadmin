"""Views for the Orders app."""
import csv
import io
from datetime import timedelta

from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

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


class UndispatchedOrdersData(TemplateView):
    """Return a list of undispatched order counts."""

    template_name = "orders/undispatched_data.html"

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


class ExportOrders(OrdersUserMixin, View):
    """Create a .csv export of order data."""

    form_class = forms.OrderListFilter
    header = [
        "order_ID",
        "date_recieved",
        "country",
        "channel",
        "tracking_number",
        "shipping_rule",
        "courier_service",
    ]

    def get(self, *args, **kwargs):
        """Return an HttpResponse contaning the export or a 404 status."""
        form = self.form_class(self.request.GET)
        if form.is_valid():
            contents = self.make_csv(form.get_queryset())
            response = HttpResponse(contents, content_type="text/csv")
            filename = f"order_export_{timezone.now().strftime('%Y-%m-%d')}.csv"
            response["Content-Disposition"] = f"attachment; filename={filename}"
            return response
        return HttpResponseNotFound()

    def make_csv(self, orders):
        """Return the export as a CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.header)
        for order in orders:
            row = self.make_row(order)
            writer.writerow(row)
        return output.getvalue()

    def make_row(self, order):
        """Return a row of order data."""
        return [
            order.order_ID,
            order.recieved_at.strftime("%Y-%m-%d"),
            order.country.name,
            order.channel.name,
            order.tracking_number,
            order.shipping_rule.name,
            order.courier_service.name,
        ]
