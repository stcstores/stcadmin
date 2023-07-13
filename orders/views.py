"""Views for the Orders app."""
from datetime import timedelta

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
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


class PackCount(OrdersUserMixin, TemplateView):
    """View for displaying pack counts and mistakes."""

    template_name = "orders/pack_count.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = forms.PackCountFilter()
        return context


class PackCountResults(OrdersUserMixin, TemplateView):
    """Return view for AJAX requests for pack counts."""

    template_name = "orders/pack_count_results.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        month = int(self.request.GET["month"])
        year = int(self.request.GET["year"])
        context["users"] = self.get_users(month=month, year=year)
        return context

    def get_users(self, month, year):
        """Return a queryset of staff annotated with pack counts and mistake counts."""
        return Staff.unhidden.order_by("first_name", "second_name").annotate(
            pack_count=Count(
                "packed_orders",
                filter=Q(
                    packed_orders__dispatched_at__month=month,
                    packed_orders__dispatched_at__year=year,
                ),
                distinct=True,
            ),
            mistake_count=Count(
                "packing_mistakes",
                filter=Q(
                    packing_mistakes__timestamp__month=month,
                    packing_mistakes__timestamp__year=year,
                ),
                distinct=True,
            ),
        )


@method_decorator(csrf_exempt, name="dispatch")
class PackingMistakes(OrdersUserMixin, ListView):
    """View for viewing packing mistakes."""

    model = models.PackingMistake
    template_name = "orders/packing_mistakes.html"
    paginate_by = 50
    orphans = 3
    form_class = forms.PackingMistakeFilterForm

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = self.form_class(self.request.GET)
        return context

    def get_queryset(self):
        """Filter the packing mistake list."""
        return self.form_class(self.request.GET).get_queryset()


class CreatePackingMistake(OrdersUserMixin, CreateView):
    """View for creating packing mistakes."""

    model = models.PackingMistake
    form_class = forms.PackingMistakeForm

    def get_success_url(self):
        """Return redirect URL."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Added a packing mistake for {self.object.user}.",
        )
        return reverse("orders:packing_mistakes")


class UpdatePackingMistake(OrdersUserMixin, UpdateView):
    """View for updating packing mistakes."""

    model = models.PackingMistake
    form_class = forms.PackingMistakeForm

    def get_success_url(self):
        """Return redirect URL."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Updated a packing mistake for {self.object.user}.",
        )
        return reverse("orders:packing_mistakes")


class DeletePackingMistake(OrdersUserMixin, DeleteView):
    """View for deleting packing mistakes."""

    model = models.PackingMistake

    def get_success_url(self):
        """Return redirect URL."""
        return reverse("orders:packing_mistakes")
