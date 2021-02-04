"""Views for the FBA app."""


import datetime

import cc_products
from ccapi import CCAPI
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView, View
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView

from fba import forms, models
from home.views import UserInGroupMixin


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
        self.product_ID = form.cleaned_data["product_ID"]
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the FBA Order create page."""
        return reverse("fba:create_order", args=[self.product_ID])


class FBAOrderCreate(FBAUserMixin, CreateView):
    """View for creating FBA orders."""

    form_class = forms.CreateFBAOrderForm
    template_name = "fba/fbaorder_form.html"

    def dispatch(self, *args, **kwargs):
        """Get product details."""
        self.get_product()
        return super().dispatch(*args, **kwargs)

    def get_product(self):
        """Return the product included in the order."""
        product_ID = self.kwargs["product_id"]
        self.product = cc_products.get_product(product_ID)

    def get_initial(self, *args, **kwargs):
        """Return initial values for the form."""
        initial = super().get_initial(*args, **kwargs)
        initial["product_SKU"] = self.product.sku
        initial["product_ID"] = self.product.id
        initial["product_name"] = self.product.full_name
        initial["product_weight"] = self.product.weight
        initial["product_hs_code"] = self.product.hs_code
        initial["product_image_url"] = self.get_image_url()
        initial["product_supplier"] = self.product.supplier.factory_name
        initial["product_purchase_price"] = self.product.purchase_price
        return initial

    def get_image_url(self):
        """Return the URL of the product's image."""
        image_data = CCAPI.get_product_images(
            range_id=self.product.range_id, product_id=self.product.id
        )
        try:
            return image_data[0].url
        except IndexError:
            return ""

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["product"] = self.product
        context["image_url"] = context["form"].initial["product_image_url"]
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
            f"Created new FBA order for product {self.object.product_SKU}.",
        )


class RepeatFBAOrder(FBAOrderCreate):
    """View for creating repeated FBA orders."""

    MAX_DUPLICATE_AGE = datetime.timedelta(days=30)

    def get(self, *args, **kwargs):
        """Duplicate the order if it is recent, otherwise use repeat order form."""
        self.get_product()
        order_age = timezone.now() - self.to_repeat.created_at
        if order_age < self.MAX_DUPLICATE_AGE:
            self.duplicate_order()
            return redirect(reverse("fba:order_list"))
        else:
            return super().get(*args, **kwargs)

    def duplicate_order(self):
        """Create a duplicate of an FBA order."""
        if (quantity_sent := self.to_repeat.quantity_sent) is not None:
            aprox_quantity = min((quantity_sent, self.product.stock_level))
        else:
            aprox_quantity = self.to_repeat.aproximate_quantity
        self.repeated_order = models.FBAOrder(
            product_SKU=self.to_repeat.product_SKU,
            product_ID=self.to_repeat.product_ID,
            product_name=self.to_repeat.product_name,
            product_weight=self.product.weight,
            product_hs_code=self.product.hs_code,
            product_asin=self.to_repeat.product_asin,
            product_image_url=self.to_repeat.product_image_url,
            product_supplier=self.to_repeat.product_supplier,
            product_purchase_price=self.to_repeat.product_purchase_price,
            region=self.to_repeat.region,
            selling_price=self.to_repeat.selling_price,
            FBA_fee=self.to_repeat.FBA_fee,
            aproximate_quantity=aprox_quantity,
            small_and_light=self.to_repeat.small_and_light,
        )
        self.repeated_order.save()

    def get_product(self):
        """Return the product included in the order."""
        self.to_repeat = get_object_or_404(models.FBAOrder, pk=self.kwargs.get("pk"))
        self.product = cc_products.get_product(self.to_repeat.product_ID)

    def get_initial(self, *args, **kwargs):
        """Return initial form values."""
        initial = super().get_initial(*args, **kwargs)
        initial["region"] = self.to_repeat.region
        initial["country"] = self.to_repeat.region.default_country
        initial["selling_price"] = self.to_repeat.selling_price
        initial["FBA_fee"] = self.to_repeat.FBA_fee
        initial["small_and_light"] = self.to_repeat.small_and_light
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

    def get_context_data(self, **kwargs):
        """Return template context."""
        context = super().get_context_data(**kwargs)
        context["product"] = cc_products.get_product(
            context["form"].instance.product_ID
        )
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


class ProductStock(View):
    """View for getting current stock information for a product."""

    def get(self, *args, **kwargs):
        """Return product stock information."""
        product_id = self.request.GET.get("product_id")
        product = CCAPI.get_product(product_id)
        stock_level = product.stock_level
        pending_stock = CCAPI.get_pending_stock(product_id)
        current_stock = stock_level - pending_stock
        return JsonResponse(
            {
                "stock_level": stock_level,
                "pending_stock": pending_stock,
                "current_stock": current_stock,
            }
        )


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
        region_name = self.request.GET.get("region")
        if region_name is not None and region_name != "":
            filter_kwargs["region__name"] = region_name
        return self.model.awaiting_fulfillment.filter(**filter_kwargs).prefetch_related(
            "region"
        )

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["regions"] = models.FBARegion.objects.all().prefetch_related(
            "default_country__country"
        )
        context["page_range"] = self.get_page_range(context["paginator"])
        context["selected_region"] = self.request.GET.get("region")
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
        self.sku = post_data.get("sku")
        self.selling_price = float(post_data.get("selling_price"))
        self.country_id = int(post_data.get("country"))
        self.purchase_price = float(post_data.get("purchase_price"))
        self.fba_fee = float(post_data.get("fba_fee"))
        country_id = int(post_data.get("country"))
        self.country = models.FBACountry.objects.get(id=country_id)
        self.exchange_rate = float(self.country.country.currency.exchange_rate)
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
        return self.country.country.currency.symbol

    def get_vat(self):
        """Return the caclulated VAT."""
        if self.country.country.vat_is_required() and not self.zero_rated:
            vat = self.selling_price / 6
            vat = round(vat, 2)
        else:
            vat = 0.0
        return vat

    def get_postage_to_fba(self):
        """Return the caclulated price to post to FBA."""
        self.postage_gbp = round(float(self.country.region.postage_price) / 100.0, 2)
        self.postage_local = round(self.postage_gbp / self.exchange_rate, 2)

    def get_postage_per_item(self):
        """Return the caclulated price per item to post to FBA."""
        postage_per_item = None
        if not self.country.region.auto_close:
            try:
                record = models.FBAShippingPrice.objects.get(product_SKU=self.sku)
                self.postage_per_item_gbp = record.price_per_item / 100
            except models.FBAShippingPrice.DoesNotExist:
                pass
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
        max_quantity = (self.country.region.max_weight * 1000) // self.product_weight
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
        product_ID = order.product_ID
        bays = CCAPI.get_bays_for_product(product_ID)
        context["bays"] = ", ".join([bay.name for bay in bays])
        context["selling_price"] = "{:.2f}".format(
            order.selling_price / 100,
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
            f"FBA order fulfilled for product {self.object.product_SKU}.",
        )

    def close_order(self):
        """Close the order and add a success message."""
        self.object.close()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"FBA order closed for product {self.object.product_SKU}.",
        )

    def update_stock(self):
        """Complete and close the order."""
        message_type, text = self.object.update_stock_level()
        messages.add_message(self.request, message_type, text)


class FBAOrderPrintout(FBAUserMixin, TemplateView):
    """View for FBA order printouts."""

    template_name = "fba/order_printout.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(models.FBAOrder, pk=self.kwargs.get("pk"))
        context["order"] = order
        context["product"] = CCAPI.get_product(order.product_ID)
        context["pending_stock"] = CCAPI.get_pending_stock(order.product_ID)
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
                product_SKU=kwargs["fba_order"].product_SKU
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


@method_decorator(csrf_exempt, name="dispatch")
class SetTrackingNumber(FBAUserMixin, View):
    """View for setting the tracking number of an FBA Order by AJAX."""

    def post(self, *args, **kwargs):
        """Set an FBA order tracking number."""
        order = get_object_or_404(models.FBAOrder, pk=self.request.POST.get("order_id"))
        tracking_number = self.request.POST.get("tracking_number")
        order.set_tracking_number(tracking_number)
        if order.closed_at is None:
            closed_at = ""
        else:
            closed_at = order.closed_at.strftime("%Y-%m-%d %H:%M")
        return JsonResponse(
            {
                "tracking_number": order.tracking_number,
                "status": order.status,
                "closed_at": closed_at,
            }
        )
