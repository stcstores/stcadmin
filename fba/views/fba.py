"""Views for managing FBA orders."""

import datetime
import json

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
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
    ProductImageLink,
    ProductRangeImageLink,
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
    form_class = forms.SelectFBAOrderProduct

    def form_valid(self, form):
        """Find the product's ID."""
        self.product = form.cleaned_data["product"]
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the FBA Order create page."""
        return reverse("fba:create_order", args=[self.product.pk])


class FBAOrderCreate(FBAUserMixin, CreateView):
    """View for creating FBA orders."""

    form_class = forms.CreateFBAOrderForm
    template_name = "fba/fbaorder_form.html"

    def dispatch(self, *args, **kwargs):
        """Return kwargs for the form."""
        self.product = get_object_or_404(BaseProduct, pk=self.kwargs["product_id"])
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_initial(self, *args, **kwargs):
        """Return initial values for the form."""
        initial = super().get_initial(*args, **kwargs)
        initial["product"] = self.product
        initial["product_weight"] = self.product.weight_grams
        initial["product_hs_code"] = self.product.hs_code
        initial["product_purchase_price"] = self.product.purchase_price
        initial["product_is_multipack"] = isinstance(
            self.product, MultipackProduct
        ) or isinstance(self.product, CombinationProduct)
        return initial

    def get_image_url(self):
        """Return the URL of the product's image."""
        image_link = ProductImageLink.objects.filter(product=self.product).first()
        if image_link is None:
            image_link = ProductRangeImageLink.objects.filter(
                product_range=self.product.product_range
            ).first()
        if image_link is None:
            return ""
        else:
            return mark_safe(image_link.image.square_image.url)

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["product"] = self.product
        try:
            stock_level = StockManager.get_stock_level(self.product)
        except Exception:
            stock_level = 0
        context["stock_level"] = stock_level
        context["existing_order_count"] = (
            models.FBAOrder.objects.filter(product=self.product)
            .exclude(status=models.FBAOrder.FULFILLED)
            .count()
        )
        return context

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


class RepeatFBAOrder(FBAOrderCreate):
    """View for creating repeated FBA orders."""

    MAX_DUPLICATE_AGE = datetime.timedelta(days=30)

    def dispatch(self, *args, **kwargs):
        """Return kwargs for the form."""
        self.get_product()
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        """Duplicate the order if it is recent, otherwise use repeat order form."""
        order_age = timezone.now() - self.to_repeat.created_at
        if order_age < self.MAX_DUPLICATE_AGE:
            self.duplicate_order()
            return redirect(reverse("fba:order_list"))
        else:
            return super().get(*args, **kwargs)

    def duplicate_order(self):
        """Create a duplicate of an FBA order."""
        stock_level = StockManager.get_stock_level(product=self.to_repeat.product)
        if (quantity_sent := self.to_repeat.quantity_sent) is not None:
            aprox_quantity = min((quantity_sent, stock_level))
        else:
            aprox_quantity = self.to_repeat.aproximate_quantity
        self.repeated_order = models.FBAOrder(
            product=self.to_repeat.product,
            product_weight=self.to_repeat.product.weight_grams,
            product_hs_code=self.to_repeat.product.hs_code,
            product_asin=self.to_repeat.product_asin,
            product_purchase_price=self.to_repeat.product_purchase_price,
            product_is_multipack=self.to_repeat.product_is_multipack,
            region=self.to_repeat.region,
            selling_price=self.to_repeat.selling_price,
            FBA_fee=self.to_repeat.FBA_fee,
            aproximate_quantity=aprox_quantity,
            small_and_light=self.to_repeat.small_and_light,
            is_fragile=self.to_repeat.is_fragile,
        )
        self.repeated_order.save()

    def get_product(self):
        """Return the product included in the order."""
        self.to_repeat = get_object_or_404(models.FBAOrder, pk=self.kwargs.get("pk"))

    def get_initial(self):
        """Return initial form values."""
        initial = super().get_initial()
        initial["region"] = self.to_repeat.region
        initial["selling_price"] = self.to_repeat.selling_price
        initial["FBA_fee"] = self.to_repeat.FBA_fee
        return initial

    def get_context_data(self, **kwargs):
        """Return template context."""
        context = super().get_context_data(**kwargs)
        context["to_repeat"] = self.to_repeat
        return context

    def set_success_message(self):
        """Set a success message."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Repeated FBA order {self.to_repeat}.",
        )


class FBAOrderUpdate(FBAUserMixin, UpdateView):
    """View for updating FBA orders."""

    form_class = forms.CreateFBAOrderForm
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
        try:
            stock_level = StockManager.get_stock_level(self.object.product)
        except Exception:
            stock_level = 0
        context["stock_level"] = stock_level
        context["product"] = self.object.product
        return context

    def get_success_url(self):
        """Redirect to the order's update page."""
        messages.add_message(self.request, messages.SUCCESS, "FBA order updated.")
        return self.object.get_absolute_url()


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


class TakeOffHold(View):
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
            .order_by_priority()
            .filter(**filter_kwargs)
            .select_related(
                "region__country",
                "product",
                "product__supplier",
                "product__product_range",
            )
            .prefetch_related(
                "tracking_numbers",
                "product__variation_option_values",
            )
        )
        if search_text := self.request.GET.get("search_term"):
            search_text = search_text.strip()
            qs = qs.filter(
                Q(
                    Q(product__sku__icontains=search_text)
                    | Q(product__product_range__name__icontains=search_text)
                    | Q(product_asin__icontains=search_text)
                    | Q(product__barcode__iexact=search_text)
                    | Q(product__sku__iexact=search_text)
                    | Q(product__product_range__sku__iexact=search_text)
                    | Q(product__supplier_sku__iexact=search_text)
                    | Q(id__iexact=search_text)
                )
            )
        return qs

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
class FBAPriceCalculator(FBAUserMixin, View):
    """View for calculating FBA profit margins."""

    def post(self, *args, **kwargs):
        """Return FBA profit margin calculations."""
        try:
            self.parse_request()
            response = {}
            response["channel_fee"] = self.get_channel_fee()
            response["currency_symbol"] = self.get_currency_symbol()
            response["vat"] = self.get_vat()
            response["postage_to_fba"] = self.postage_gbp
            response["postage_per_item"] = self.postage_per_item_gbp
            response["profit"] = round(self.get_profit() * self.exchange_rate, 2)
            response["percentage"] = self.get_percentage()
            response["purchase_price"] = self.get_purchase_price()
            max_quantity, max_quantity_no_stock = self.get_max_quantity()
            response["max_quantity"] = max_quantity
            response["max_quantity_no_stock"] = max_quantity_no_stock
            return JsonResponse(response)
        except Exception:
            return HttpResponseBadRequest()

    def parse_request(self):
        """Get request parameters from POST."""
        post_data = self.request.POST
        self.selling_price = float(post_data.get("selling_price"))
        self.country_id = int(post_data.get("region"))
        self.purchase_price = float(post_data.get("purchase_price"))
        self.fba_fee = float(post_data.get("fba_fee"))
        region_id = int(post_data.get("region"))
        self.region = models.FBARegion.objects.get(id=region_id)
        self.exchange_rate = float(self.region.country.currency.exchange_rate())
        self.product_weight = int(post_data.get("weight"))
        self.stock_level = int(post_data.get("stock_level"))
        self.zero_rated = post_data.get("zero_rated") == "true"
        try:
            self.quantity = int(post_data.get("quantity"))
        except ValueError:
            self.quantity, _ = self.get_max_quantity()
        self.get_postage_to_fba()
        self.get_profit()

    def get_channel_fee(self):
        """Return the caclulated channel fee."""
        channel_fee = self.selling_price * 0.15
        return round(channel_fee, 2)

    def get_currency_symbol(self):
        """Return the currency symbol."""
        return self.region.country.currency.symbol

    def get_vat(self):
        """Return the caclulated VAT."""
        if self.region.country.vat_is_required() == self.region.country.VAT_NEVER:
            return 0.0
        elif (
            self.region.country.vat_is_required() != self.region.country.VAT_ALWAYS
            and self.zero_rated
        ):
            return 0.0
        else:
            vat = self.selling_price / 6
            vat = round(vat, 2)
        return vat

    def get_postage_to_fba(self):
        """Return the caclulated price to post to FBA."""
        shipped_weight = self.product_weight * self.quantity
        self.postage_gbp = round(
            float(self.region.calculate_shipping(shipped_weight)) / 100.0,
            2,
        )
        self.postage_local = round(self.postage_gbp / self.exchange_rate, 2)

    def get_postage_per_item(self):
        """Return the caclulated price per item to post to FBA."""
        postage_per_item = None
        if postage_per_item is None:
            self.postage_per_item_gbp = round(self.postage_gbp / int(self.quantity), 2)
        self.postage_per_item_local = round(
            self.postage_per_item_gbp / self.exchange_rate, 2
        )

    def get_profit(self):
        """Return the calculated per item profit."""
        self.get_postage_per_item()
        profit = self.selling_price - sum(
            [
                self.postage_per_item_local,
                self.get_channel_fee(),
                self.get_vat(),
                self.get_purchase_price(),
                self.fba_fee,
            ]
        )
        return profit

    def get_percentage(self):
        """Return the percentage fo the sale price that is profit."""
        percentage = (self.get_profit() / self.selling_price) * 100
        return round(percentage, 2)

    def get_purchase_price(self):
        """Return the purchase price in local currency."""
        purchase_price = self.purchase_price / self.exchange_rate
        return round(purchase_price, 2)

    def get_max_quantity(self):
        """Return the maximum number of the product that can be sent."""
        max_quantity = (self.region.max_weight * 1000) // self.product_weight
        return min((max_quantity, self.stock_level)), max_quantity


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
        context["shipment_packages"] = models.FBAShipmentPackage.objects.filter(
            fba_order=context["form"].instance
        )
        return context

    def form_valid(self, form):
        """Save the user fulfilling the order."""
        return_value = super().form_valid(form)
        form.save()
        if form.instance.details_complete():
            collection_booked = "collection_booked" in self.request.POST
            if self.object.region.auto_close:
                self.close_order()
                self.fulfill_order()
            elif collection_booked:
                self.close_order()
            else:
                self.fulfill_order()
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
        message_type, text = self.object.update_stock_level(user=self.request.user)
        messages.add_message(self.request, message_type, text)


class FBAOrderPrintout(FBAUserMixin, TemplateView):
    """View for FBA order printouts."""

    template_name = "fba/order_printout.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(models.FBAOrder, pk=self.kwargs.get("pk"))
        product = get_object_or_404(BaseProduct, sku=order.product.sku)
        context["order"] = order
        context["product"] = product
        try:
            stock_level_info = StockManager.stock_level_info(product.sku)
        except Exception:
            context["stock_level"] = "ERROR"
            context["pending_stock"] = "ERROR"
        else:
            context["stock_level"] = stock_level_info.stock_level
            context["pending_stock"] = stock_level_info.in_orders
        context["bays"] = (
            product.product_bay_links.select_related("bay")
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


class ShippingPrice(FBAUserMixin, FormView):
    """View for adding correct shipping prices."""

    form_class = forms.ShippingPriceForm
    template_name = "fba/shipping_price.html"

    def get_form_kwargs(self, *args, **kwargs):
        """Add the FBA order to the form kwargs."""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["fba_order"] = get_object_or_404(
            models.FBAOrder, id=self.kwargs.get("pk")
        )
        try:
            kwargs["instance"] = models.FBAShippingPrice.objects.get(
                product_SKU=kwargs["fba_order"].product.sku
            )
        except models.FBAShippingPrice.DoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        """Get the FBA Order from the form."""
        self.fba_order = form.fba_order
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the url to redirect to on successful submission."""
        return self.fba_order.get_absolute_url()


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
        product_ids = orders.values_list("product", flat=True)
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
