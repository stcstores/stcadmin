"""Views for managing FBA orders."""

import datetime
import json
from collections import defaultdict

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView, View
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView

from fba import forms, models
from home.views import UserInGroupMixin
from inventory.models import (
    BaseProduct,
    CombinationProduct,
    MultipackProduct,
    ProductBayLink,
)
from linnworks.models import StockManager


class FBAUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the fba group."""

    groups = ["fba"]


class Index(FBAUserMixin, TemplateView):
    """Landing page for the FBA app."""

    template_name = "fba/index.html"


class SelectFBAOrderProduct(FBAUserMixin, FormView):
    """View for selecting a product for and FBA order."""

    template_name = "fba/select_order_product.html"
    form_class = forms.SelectFBAOrderProductForm

    def form_valid(self, form):
        """Find the product's ID."""
        self.product = form.cleaned_data["product"]
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the FBA Order create page."""
        return reverse("fba:create_order", args=[self.product.pk])


class FBAOrderCreate(FBAUserMixin, CreateView):
    """View for creating FBA orders."""

    form_class = forms.FBAOrderForm
    template_name = "fba/fbaorder_form.html"

    def get_initial(self, *args, **kwargs):
        """Return initial values for the form."""
        initial = super().get_initial(*args, **kwargs)
        product = get_object_or_404(BaseProduct, pk=self.kwargs["product_id"])
        initial["product"] = product
        initial["product_weight"] = product.weight_grams
        initial["product_hs_code"] = product.hs_code
        initial["product_purchase_price"] = product.purchase_price
        initial["product_is_multipack"] = isinstance(
            product, MultipackProduct
        ) or isinstance(product, CombinationProduct)
        return initial

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        product = get_object_or_404(BaseProduct, pk=self.kwargs["product_id"])
        context["product"] = product
        context["stock_level"] = self.get_stock_level(product)
        context["existing_order_count"] = (
            models.FBAOrder.objects.filter(product=product)
            .exclude(status=models.FBAOrder.FULFILLED)
            .count()
        )
        return context

    @staticmethod
    def get_stock_level(product):
        """Return the product's stock level."""
        try:
            return StockManager.get_stock_level(product)
        except Exception:
            return 0

    def get_success_url(self):
        """Redirect to the order's update page."""
        self.set_success_message()
        return self.object.get_absolute_url()

    def set_success_message(self):
        """Set a success message."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Created new FBA order for product {self.object.product.sku}.",
        )


class FBAOrderUpdate(FBAUserMixin, UpdateView):
    """View for updating FBA orders."""

    form_class = forms.FBAOrderForm
    model = models.FBAOrder
    template_name = "fba/fbaorder_form.html"

    def get_initial(self):
        """Return initial values for the form."""
        initial = super().get_initial()
        initial["country"] = self.object.region.country
        return initial

    def get_context_data(self, **kwargs):
        """Return template context."""
        context = super().get_context_data(**kwargs)
        context["stock_level"] = self.get_stock_level(self.object.product)
        context["product"] = self.object.product
        return context

    @staticmethod
    def get_stock_level(product):
        """Return the product's stock level."""
        try:
            return StockManager.get_stock_level(product)
        except Exception:
            return 0

    def get_success_url(self):
        """Redirect to the order's update page."""
        messages.add_message(self.request, messages.SUCCESS, "FBA order updated.")
        return self.object.get_absolute_url()


class RepeatFBAOrder(FBAUserMixin, RedirectView):
    """View for creating repeated FBA orders."""

    MAX_DUPLICATE_AGE = datetime.timedelta(days=30)

    def get_redirect_url(self, *args, **kwargs):
        """Duplicate the order if it is recent, otherwise use repeat order form."""
        order = get_object_or_404(models.FBAOrder, pk=self.kwargs.get("pk"))
        if timezone.now() - order.created_at < self.MAX_DUPLICATE_AGE:
            self.duplicate_order(order)
            self.set_success_message(order)
        else:
            self.set_error_message(order)
        return reverse("fba:order_list")

    def duplicate_order(self, order):
        """Create a duplicate of an FBA order."""
        stock_level = StockManager.get_stock_level(product=order.product)
        order.duplicate(stock_level=stock_level)

    def set_success_message(self, order):
        """Set a success message."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Repeated FBA order {order}.",
        )

    def set_error_message(self, order):
        """Set an error message."""
        messages.add_message(
            self.request,
            messages.ERROR,
            f"FBA order {order} is too old to be repeated.",
        )


class OrderList(FBAUserMixin, ListView):
    """Display a filterable list of orders."""

    template_name = "fba/fba_order_list.html"
    model = models.FBAOrder
    paginate_by = 50
    orphans = 3
    form_class = forms.FBAOrderFilter

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


class OnHold(FBAUserMixin, ListView):
    """Display a filterable list of orders."""

    template_name = "fba/on_hold.html"
    model = models.FBAOrder
    paginate_by = 50
    orphans = 3
    form_class = forms.OnHoldOrderFilter

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
        context["page_range"] = self.get_page_range(context["paginator"])
        context["form"] = self.form
        return context

    def get_page_range(self, paginator):
        """Return a list of pages to link to."""
        if paginator.num_pages < 11:
            return list(range(1, paginator.num_pages + 1))
        else:
            return list(range(1, 11)) + [paginator.num_pages]


class StoppedFBAOrders(FBAUserMixin, ListView):
    """Display a filterable list of orders."""

    template_name = "fba/stopped.html"
    model = models.FBAOrder
    paginate_by = 50
    orphans = 3
    form_class = forms.StoppedOrderFilter

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
        context["page_range"] = self.get_page_range(context["paginator"])
        context["form"] = self.form
        return context

    def get_page_range(self, paginator):
        """Return a list of pages to link to."""
        if paginator.num_pages < 11:
            return list(range(1, paginator.num_pages + 1))
        else:
            return list(range(1, 11)) + [paginator.num_pages]


class TakeOffHold(FBAUserMixin, View):
    """View for takeing order off hold."""

    def get(self, *args, **kwargs):
        """Take order off hold."""
        pk = self.request.GET.get("order_id")
        order = get_object_or_404(models.FBAOrder, pk=pk)
        order.on_hold = False
        order.save()
        return HttpResponse("ok")


class Awaitingfulfillment(FBAUserMixin, ListView):
    """Display a filterable list of orders."""

    template_name = "fba/awaiting_fulfillment.html"
    model = models.FBAOrder
    paginate_by = 50
    orphans = 3

    def get_queryset(self):
        """Return a queryset of orders awaiting fulillment."""
        filter_kwargs = {}
        if region_id := self.request.GET.get("region"):
            filter_kwargs["region__id"] = region_id
        if status := self.request.GET.get("status"):
            filter_kwargs["status"] = status
        qs = (
            self.model.objects.awaiting_fulfillment()
            .filter(**filter_kwargs)
            .select_related(
                "region__country",
            )
            .prefetch_related(
                "product",
                "product__supplier",
                "product__product_range",
                "tracking_numbers",
                "product__variation_option_values",
            )
        )
        if search_text := self.request.GET.get("search_term"):
            search_text = search_text.strip()
            qs = qs.filter(
                Q(
                    Q(product__sku__iexact=search_text)
                    | Q(product__product_range__name__icontains=search_text)
                    | Q(product_asin__icontains=search_text)
                    | Q(product__barcode__iexact=search_text)
                    | Q(product__product_range__sku__iexact=search_text)
                    | Q(product__supplier_sku__iexact=search_text)
                    | Q(id__iexact=search_text)
                )
            )
        return qs.order_by_priority()

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["regions"] = models.FBARegion.objects.filter(
            active=True
        ).prefetch_related("country")
        context["page_range"] = self.get_page_range(context["paginator"])
        if region := self.request.GET.get("region"):
            context["selected_region"] = int(region)
        context["statuses"] = [
            models.FBAOrder.READY,
            models.FBAOrder.PRINTED,
            models.FBAOrder.NOT_PROCESSED,
        ]
        return context

    def get_page_range(self, paginator):
        """Return a list of pages to link to."""
        if paginator.num_pages < 11:
            return list(range(1, paginator.num_pages + 1))
        else:
            return list(range(1, 11)) + [paginator.num_pages]


@method_decorator(csrf_exempt, name="dispatch")
class FBAPriceCalculatorView(FBAUserMixin, View):
    """View for calculating FBA profit margins."""

    def post(self, *args, **kwargs):
        """Return FBA profit margin calculations."""
        try:
            calculator = models.FBAPriceCalculator(
                selling_price=float(self.request.POST.get("selling_price")),
                region=get_object_or_404(
                    models.FBARegion, pk=int(self.request.POST.get("region"))
                ),
                purchase_price=float(self.request.POST.get("purchase_price")),
                fba_fee=float(self.request.POST.get("fba_fee")),
                product_weight=int(self.request.POST.get("weight")),
                stock_level=int(self.request.POST.get("stock_level")),
                zero_rated=self.request.POST.get("zero_rated") == "true",
                quantity=int(self.request.POST.get("quantity")),
            )
            calculator.calculate()
            return JsonResponse(calculator.to_dict(), safe=False)
        except Exception:
            return HttpResponseBadRequest()


class FulfillFBAOrder(FBAUserMixin, UpdateView):
    """View for creating FBA orders."""

    model = models.FBAOrder
    form_class = forms.FulfillFBAOrderForm
    template_name = "fba/fulfill_fba_order.html"

    def get_context_data(self, *args, **kwargs):
        """Add the bay list to the context."""
        context = super().get_context_data(*args, **kwargs)
        order = context["form"].instance
        sku = order.product.sku
        bays = (
            ProductBayLink.objects.filter(product__sku=sku)
            .select_related("bay")
            .order_by()
            .distinct()
            .values_list("bay__name", flat=True)
        )
        context["bays"] = ", ".join([bay for bay in bays])
        context["selling_price"] = "{:.2f}".format(
            order.selling_price / 100,
        )
        return context

    def form_valid(self, form):
        """Save the user fulfilling the order."""
        object_before_update = get_object_or_404(self.model, pk=self.object.pk)
        order_was_complete = object_before_update.details_complete()
        return_value = super().form_valid(form)
        form.save()
        order_is_complete = form.instance.details_complete()
        if order_is_complete and not order_was_complete:
            if self.object.region.auto_close:
                self.close_order()
            self.fulfill_order()
        elif order_is_complete and "collection_booked" in self.request.POST:
            self.close_order()
        return return_value

    def get_success_url(self):
        """Redirect to the order list."""
        return self.object.get_fulfillment_url()

    def fulfill_order(self):
        """Mark an order as fulfilled and update stock."""
        self.update_stock()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"FBA order fulfilled for product {self.object.product.sku}.",
        )

    def close_order(self):
        """Close the order and add a success message."""
        self.object.close()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"FBA order closed for product {self.object.product.sku}.",
        )

    def update_stock(self):
        """Complete and close the order."""
        if settings.DEBUG is True:
            messages.add_message(
                self.request, messages.WARNING, "Stock update skipped: DEBUG mode."
            )
        elif self.object.update_stock_level_when_complete is False:
            messages.add_message(
                self.request,
                messages.WARNING,
                (
                    "Set to skip stock update, the stock level for "
                    f"{self.object.product.sku} is unchanged."
                ),
            )
        else:
            try:
                stock_level, new_stock_level = self._update_stock()
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    (
                        f"Changed stock level for {self.object.product.sku} from {stock_level} "
                        f"to {new_stock_level}"
                    ),
                )
            except Exception:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    (
                        f"Stock Level failed to update for {self.object.product.sku}, "
                        "please check stock level."
                    ),
                )

    def _update_stock(self):
        stock_level = StockManager.get_stock_level(self.object.product)
        new_stock_level = stock_level - self.object.quantity_sent
        change_source = f"Updated by FBA order pk={self.object.pk}"
        StockManager.set_stock_level(
            product=self.object.product,
            user=self.request.user,
            new_stock_level=new_stock_level,
            change_source=change_source,
        )
        return stock_level, new_stock_level


class FBAOrderPrintout(FBAUserMixin, TemplateView):
    """View for FBA order printouts."""

    template_name = "fba/order_printout.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(models.FBAOrder, pk=self.kwargs.get("pk"))
        context["order"] = order
        context["product"] = order.product
        try:
            stock_level_info = StockManager.stock_level_info(order.product.sku)
        except Exception:
            context["stock_level"] = "ERROR"
            context["pending_stock"] = "ERROR"
        else:
            context["stock_level"] = stock_level_info.stock_level
            context["pending_stock"] = stock_level_info.in_orders
        context["bays"] = (
            order.product.product_bay_links.select_related("bay")
            .order_by()
            .distinct()
            .values_list("bay__name", flat=True)
        )
        order.printed = True
        order.save()
        return context


class UnmarkPrinted(FBAUserMixin, RedirectView):
    """View to unmark FBA orders as printed."""

    def get_redirect_url(self, *args, **kwargs):
        """Unmark an FBA order as printed and return to it's fulfillment page."""
        order = get_object_or_404(models.FBAOrder, pk=self.kwargs.get("pk"))
        order.printed = False
        order.save()
        return self.request.GET.get("next")


class DeleteFBAOrder(FBAUserMixin, DeleteView):
    """View to delete FBA orders."""

    model = models.FBAOrder

    def get_object(self):
        """Prevent deletion of in progress or completed FBA orders."""
        order = get_object_or_404(models.FBAOrder, pk=self.kwargs.get("pk"))
        if order.status == order.FULFILLED:
            raise PermissionDenied()
        return order

    def get_success_url(self):
        """Return the URL to redirect to after a succesfull deletion."""
        return reverse("fba:order_list")


class StopFBAOrder(FBAUserMixin, UpdateView):
    """View for marking FBA Orders as stopped."""

    model = models.FBAOrder
    form_class = forms.StopFBAOrderForm
    template_name = "fba/stop_fba_order_form.html"

    def get_initial(self):
        """Return initial values for the form."""
        initial = super().get_initial()
        initial["is_stopped"] = True
        initial["stopped_at"] = timezone.now().strftime("%d/%m/%Y")
        return initial

    def get_success_url(self):
        """Return URL to redirect to after successful update."""
        return reverse("fba:update_fba_order", args=[self.object.pk])


class UnstopFBAOrder(FBAUserMixin, RedirectView):
    """Unmark an FBA Order as stopped."""

    def get_redirect_url(self, *args, **kwargs):
        """Unmark an FBA Order as stopped."""
        order = get_object_or_404(models.FBAOrder, id=self.kwargs["pk"])
        order.is_stopped = False
        order.save()
        return reverse("fba:update_fba_order", args=[order.pk])


class PrioritiseOrder(FBAUserMixin, View):
    """View for prioritising FBA orders."""

    def get(self, request, *args, **kwargs):
        """Make an FBA order the top priority."""
        order = get_object_or_404(models.FBAOrder, pk=int(request.GET["order_id"]))
        order.prioritise()
        return HttpResponse("ok")


class EditTrackingNumbers(FBAUserMixin, UpdateView):
    """View for updating FBA order tracking numbers."""

    model = models.FBAOrder
    template_name = "fba/tracking_numbers.html"
    form_class = forms.TrackingNumbersForm

    def get_success_url(self):
        """Return the success URL."""
        messages.add_message(
            self.request, messages.SUCCESS, "Tracking numbers updated."
        )
        return reverse("fba:edit_tracking_numbers", kwargs={"pk": self.object.id})


@method_decorator(csrf_exempt, name="dispatch")
class GetStockLevels(FBAUserMixin, View):
    """View for getting stock levels for FBA Orders by AJAX."""

    def post(self, *args, **kwargs):
        """Get stock levels for FBA orders."""
        order_ids = json.loads(self.request.body)["order_ids"]
        orders = models.FBAOrder.objects.filter(pk__in=order_ids)
        product_ids = list(orders.values_list("product", flat=True))
        products = BaseProduct.objects.filter(id__in=product_ids)
        stock_levels = StockManager.get_stock_levels(products)
        output = {}
        for order in orders:
            stock_level = stock_levels[order.product.sku]
            output[order.pk] = {
                "available": stock_level.available,
                "in_orders": stock_level.in_orders,
                "total": stock_level.stock_level,
            }
        return JsonResponse(output)


class ShippingCalculator(FBAUserMixin, TemplateView):
    """View for FBA shipping calculator."""

    template_name = "fba/shipping_calculator.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["regions"] = models.FBARegion.objects.filter(active=True)
        return context


class FBAProductProfit(FBAUserMixin, TemplateView):
    """View for FBA product profit calculations."""

    template_name = "fba/profit.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        product = get_object_or_404(BaseProduct, pk=self.kwargs["pk"])
        context["product"] = product
        context["profit_calculations"] = models.FBAProfit.objects.current().filter(
            product=product
        )
        return context


class FBAProfitList(FBAUserMixin, TemplateView):
    """View for listing all FBA product profit calculations."""

    template_name = "fba/profit_list.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["profit_calculations"] = defaultdict(list)
        fees = (
            models.FBAProfit.objects.current()
            .order_by("product")
            .select_related(
                "product",
                "product__product_range",
                "region",
                "region__country",
                "last_order",
            )
        )
        for fee in fees:
            context["profit_calculations"][fee.product].append(fee)
        context["profit_calculations"] = dict(context["profit_calculations"])
        return context
