"""Views for the Orders app."""
import csv
import io
from datetime import timedelta

from django.db.models import Count, Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, reverse
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from feedback.models import Feedback, UserFeedback
from home.models import CloudCommerceUser
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


class ExportOrders(OrdersUserMixin, View):
    """Create a .csv export of order data."""

    form_class = forms.OrderListFilter
    header = [
        "order_id",
        "date_recieved",
        "date_dispatched",
        "country",
        "channel",
        "tracking_number",
        "shipping_service",
        "currency",
        "total_paid",
        "total_paid_GBP",
        "weight",
        "channel_fee",
        "purchase_price",
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
        if order.is_dispatched():
            dispatched_at = order.dispatched_at.strftime("%Y-%m-%d")
        else:
            dispatched_at = "UNDISPATCHED"
        weight = order.total_weight()
        channel_fee = order.channel_fee_paid()
        purchase_price = order.purchase_price()
        if order.shipping_service is None:
            shipping_service = None
        else:
            shipping_service = order.shipping_service.name
        return [
            order.order_id,
            order.recieved_at.strftime("%Y-%m-%d"),
            dispatched_at,
            order.country.name,
            order.channel.name,
            order.tracking_number,
            shipping_service,
            order.currency.code,
            self.format_currency(order.total_paid),
            self.format_currency(order.total_paid_GBP),
            weight,
            self.format_currency(channel_fee),
            self.format_currency(purchase_price),
        ]

    def format_currency(self, price):
        """Return a price as a formatted string."""
        if price is None:
            return None
        return f"{price / 100:.2f}"


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


class RefundList(OrdersUserMixin, ListView):
    """Display a filterable list of orders."""

    template_name = "orders/refunds/refund_list.html"
    model = models.Refund
    paginate_by = 50
    orphans = 3
    form_class = forms.RefundListFilter

    def get(self, *args, **kwargs):
        """Instanciate the form."""
        self.form = self.form_class(self.request.GET)
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Return a queryset of orders based on GET data."""
        if self.form.is_valid():
            return (
                self.form.get_queryset()
                .prefetch_related(
                    "products",
                    "order__productsale_set",
                    "order__packingrecord",
                )
                .select_related("order", "order__channel", "order")
                .order_by("-order__dispatched_at")
            )
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


class CreateRefund(OrdersUserMixin, FormView):
    """View for selecting orders for which a refund will be created."""

    template_name = "orders/refunds/create_refund_order_select.html"
    form_class = forms.CreateRefund

    def form_valid(self, form):
        """Get the submitted order ID."""
        order = form.cleaned_data["order"]
        refund_type = form.cleaned_data["refund_type"]
        refund_class = form.refund_types[refund_type]
        products = order.productsale_set.all()
        if products.count() == 1 and products[0].quantity == 1:
            product_sale = products.first()
            refunds = refund_class.from_order(order, [(product_sale, 1)])
            return HttpResponseRedirect(refunds[0].get_absolute_url())
        else:
            return HttpResponseRedirect(
                reverse("orders:select_refund_products", args=[refund_type, order.pk])
            )


class Refund(OrdersUserMixin, TemplateView):
    """View for refunds."""

    template_name = "orders/refunds/refund.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        refund = get_object_or_404(models.Refund, pk=self.kwargs["pk"])
        context["refund"] = refund
        context["order"] = refund.order
        refund_products = refund.products.all()
        context["products"] = refund_products
        context["other_products"] = refund.order.productsale_set.exclude(
            id__in=[refund_product.product.id for refund_product in refund_products]
        )
        context["packing_record"] = get_object_or_404(
            models.PackingRecord, order=refund.order
        )
        context["refund_images"] = models.RefundImage.objects.filter(
            refund=refund, product_refund__isnull=True
        )
        if isinstance(refund, models.PackingMistakeRefund):
            try:
                context["feedback"] = UserFeedback.objects.get(
                    feedback_type__name="Packing Mistake",
                    order_id=refund.order.order_id,
                )
            except UserFeedback.DoesNotExist:
                context["feedback"] = None
        return context


class MarkRefundContacted(OrdersUserMixin, RedirectView):
    """View for marking refunds as contacted."""

    def get_redirect_url(self, pk):
        """Mark the refund as contacted and redirect to it's page."""
        refund = get_object_or_404(models.Refund, id=pk)
        refund.contact_contacted = True
        refund.save()
        return refund.get_absolute_url()


class MarkRefundAccepted(OrdersUserMixin, RedirectView):
    """View for marking refunds as rejected."""

    def get_redirect_url(self, pk):
        """Mark the refund as contacted and redirect to it's page."""
        if self.request.method == "POST":
            raise Http404
        refund = get_object_or_404(models.Refund, id=pk)
        refund.refund_amount = int(float(self.request.GET["refund_amount"]) * 100)
        refund.refund_accepted = True
        refund.save()
        return refund.get_absolute_url()


class MarkRefundRejected(OrdersUserMixin, RedirectView):
    """View for marking refunds as rejected."""

    def get_redirect_url(self, pk):
        """Mark the refund as contacted and redirect to it's page."""
        refund = get_object_or_404(models.Refund, id=pk)
        refund.refund_accepted = False
        refund.save()
        return refund.get_absolute_url()


class SelectRefundProducts(OrdersUserMixin, FormView):
    """View for creating refunds with multiple products."""

    form_class = forms.RefundProductFormset
    template_name = "orders/refunds/product_form.html"

    def get_form_kwargs(self, *args, **kwargs):
        """Return kwargs for the formset."""
        self.refund_type = self.kwargs.get("refund_type")
        self.refund_class = forms.CreateRefund.refund_types[self.refund_type]
        self.order = get_object_or_404(models.Order, pk=self.kwargs.get("order_pk"))
        products = self.order.productsale_set.all()
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs["form_kwargs"] = [{"product_sale": product} for product in products]
        return form_kwargs

    def form_valid(self, formset):
        """Create a refund."""
        products = [
            (form.product_sale, form.cleaned_data["quantity"])
            for form in formset
            if form.cleaned_data["quantity"] > 0
        ]
        self.refunds = self.refund_class.from_order(self.order, products)
        return super().form_valid(formset)

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["formset"] = context.pop("form")
        return context

    def get_success_url(self):
        """Return the URL to redirect to after a succesfull form submission."""
        if len(self.refunds) == 1:
            return self.refunds[0].get_absolute_url()
        return reverse("orders:refund_list") + f"?order_id={self.order.order_id}"


class AddRefundImages(OrdersUserMixin, RedirectView):
    """View for adding images to refunds."""

    def get_redirect_url(self, refund_pk, product_pk=None):
        """Create refund images and redirect to the images page."""
        refund = get_object_or_404(models.Refund, pk=refund_pk)
        if product_pk is not None:
            product_refund = get_object_or_404(models.ProductRefund, pk=product_pk)
        else:
            product_refund = None
        images = self.request.FILES.getlist("images")
        for image in images:
            refund_image = models.RefundImage(
                refund=refund,
                product_refund=product_refund,
                image=image,
            )
            refund_image.save()
        return refund.get_absolute_url()


class DeleteRefundImage(OrdersUserMixin, DeleteView):
    """View for deleting refund images."""

    model = models.RefundImage
    template_name = "orders/refunds/confirm_refund_image_delete.html"

    def get_success_url(self):
        """Return the URL to return to after deleting the image."""
        return self.object.refund.get_absolute_url()


class SetRefundNotes(OrdersUserMixin, RedirectView):
    """View for setting refund notes."""

    def get_redirect_url(self, pk):
        """Set the refund notes field and redirect to it's page."""
        refund = get_object_or_404(models.Refund, pk=pk)
        note_text = self.request.GET.get("notes") or ""
        refund.notes = note_text
        refund.save()
        return refund.get_absolute_url()


class ExportRefunds(OrdersUserMixin, View):
    """Create a .csv export of order data."""

    form_class = forms.RefundListFilter
    header = [
        "order_id",
        "refund_reason",
        "date_recieved",
        "date_dispatched",
        "country",
        "channel",
        "tracking_number",
        "courier",
        "supplier",
        "contacted",
        "accepted",
        "amount",
    ]

    def get(self, *args, **kwargs):
        """Return an HttpResponse contaning the export or a 404 status."""
        form = self.form_class(self.request.GET)
        if form.is_valid():
            contents = self.make_csv(form.get_queryset())
            response = HttpResponse(contents, content_type="text/csv")
            filename = f"refunds_export_{timezone.now().strftime('%Y-%m-%d')}.csv"
            response["Content-Disposition"] = f"attachment; filename={filename}"
            return response
        return HttpResponseNotFound()

    def make_csv(self, refunds):
        """Return the export as a CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.header)
        for refund in refunds:
            row = self.make_row(refund)
            writer.writerow(row)
        return output.getvalue()

    def make_row(self, refund):
        """Return a row of order data."""
        return [
            refund.order.order_id,
            refund.reason(),
            refund.order.recieved_at.strftime("%Y-%m-%d"),
            refund.order.dispatched_at.strftime("%Y-%m-%d"),
            refund.order.country.name,
            refund.order.channel.name,
            refund.order.tracking_number,
            getattr(refund, "courier", ""),
            getattr(refund, "supplier", ""),
            getattr(refund, "contact_contacted", ""),
            getattr(refund, "refund_accepted", ""),
            self.format_currency(getattr(refund, "refund_amount", None)),
        ]

    def format_currency(self, price):
        """Return a price as a formatted string."""
        if price is None:
            return None
        return f"{price / 100:.2f}"


class AddPackingMistakeForRefund(OrdersUserMixin, RedirectView):
    """View for adding packing mistakes for a refund."""

    def get_redirect_url(self, refund_pk):
        """Create feedback and redirect to refund page."""
        if self.request.method == "POST":
            raise Http404
        refund = get_object_or_404(models.PackingMistakeRefund, pk=refund_pk)
        packing_record = get_object_or_404(models.PackingRecord, order=refund.order)
        feedback_type = Feedback.objects.get(name="Packing Mistake")
        feedback = UserFeedback(
            user=packing_record.packed_by,
            feedback_type=feedback_type,
            order_id=refund.order.order_id,
        )
        feedback.save()
        return refund.get_absolute_url()


class DeleteRefund(OrdersUserMixin, View):
    """View for deleting refunds."""

    def get(self, *args, **kwargs):
        """Delete a refund."""
        refund = get_object_or_404(models.Refund, pk=kwargs.get("refund_pk"))
        try:
            refund.delete()
        except Exception:
            return HttpResponseNotFound
        return HttpResponse("ok")


class SetParcelReturnedForRefund(OrdersUserMixin, RedirectView):
    """View for setting the parcel returned status on Lost In Post refunds."""

    def get_redirect_url(self, refund_pk):
        """Set the returned field of the refund to True and redirect to it's page."""
        refund = get_object_or_404(models.LostInPostRefund, id=refund_pk)
        refund.returned = True
        refund.save()
        return refund.get_absolute_url()


class SetParcelNotReturnedForRefund(OrdersUserMixin, RedirectView):
    """View for setting the parcel returned status on Lost In Post refunds."""

    def get_redirect_url(self, refund_pk):
        """Set the returned field of the refund to False and redirect to it's page."""
        refund = get_object_or_404(models.LostInPostRefund, id=refund_pk)
        refund.returned = False
        refund.save()
        return refund.get_absolute_url()


class MarkRefundPartial(OrdersUserMixin, RedirectView):
    """View for setting refunds as partial."""

    def get_redirect_url(self, refund_pk):
        """Set a refund as partial."""
        refund = get_object_or_404(models.Refund, id=refund_pk)
        refund.is_partial = True
        refund.save()
        return refund.get_absolute_url()


class TrackingWarnings(OrdersUserMixin, TemplateView):
    """View for tracking warnings."""

    template_name = "orders/tracking_warnings.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = forms.TrackingWarningFilter()
        return context
