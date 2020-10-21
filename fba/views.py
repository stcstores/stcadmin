"""Views for the FBA app."""

import cc_products
from ccapi import CCAPI
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView, View
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, FormView, UpdateView

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

    def get_initial(self, *args, **kwargs):
        """Return initial values for the form."""
        initial = super().get_initial(*args, **kwargs)
        product_ID = self.kwargs["product_id"]
        self.product = cc_products.get_product(product_ID)
        initial["product_SKU"] = self.product.sku
        initial["product_ID"] = product_ID
        initial["product_name"] = self.product.full_name
        return initial

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["product"] = self.product
        return context

    def get_success_url(self):
        """Redirect to the order's update page."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Created new FBA order for product {self.object.product_SKU}.",
        )
        return self.object.get_absolute_url()


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


class AwaitingFullfilment(FBAUserMixin, ListView):
    """Display a filterable list of orders."""

    template_name = "fba/awaiting_fulfillment.html"
    model = models.FBAOrder
    paginate_by = 50
    orphans = 3

    def get_queryset(self):
        """Return a queryset of orders awaiting fulillment."""
        return self.model.awaiting_fulfillment.all()

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["page_range"] = self.get_page_range(context["paginator"])
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
            response["postage_to_fba"] = self.get_postage_to_fba()
            response["postage_per_item"] = self.get_postage_per_item()
            response["profit"] = self.get_profit()
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
        self.country_id = int(post_data.get("country"))
        self.purchase_price = float(post_data.get("purchase_price"))
        self.fba_fee = float(post_data.get("fba_fee"))
        country_id = int(post_data.get("country"))
        self.country = models.FBACountry.objects.get(id=country_id)
        self.exchange_rate = float(self.country.country.currency.exchange_rate)
        self.product_weight = int(post_data.get("weight"))
        self.stock_level = int(post_data.get("stock_level"))
        try:
            self.quantity = int(post_data.get("quantity"))
        except ValueError:
            self.quantity, _ = self.get_max_quantity()

    def get_channel_fee(self):
        """Return the caclulated channel fee."""
        channel_fee = self.selling_price * 0.15
        return round(channel_fee, 2)

    def get_currency_symbol(self):
        """Return the currency symbol."""
        return self.country.country.currency.symbol

    def get_vat(self):
        """Return the caclulated VAT."""
        if self.country.country.vat_is_required():
            vat = self.selling_price / 6
            vat = round(vat, 2)
        else:
            vat = 0.0
        return vat

    def get_postage_to_fba(self):
        """Return the caclulated price to post to FBA."""
        postage_to_fba = float(self.country.region.postage_price) / 100.0
        return round(postage_to_fba, 2)

    def get_postage_per_item(self):
        """Return the caclulated price per item to post to FBA."""
        postage_per_item = self.get_postage_to_fba() / int(self.quantity)
        return round(postage_per_item, 2)

    def get_profit(self):
        """Return the calculated per item profit."""
        profit = self.selling_price - sum(
            [
                self.get_postage_per_item(),
                self.get_channel_fee(),
                self.get_vat(),
                self.get_purchase_price(),
                self.fba_fee,
            ]
        )
        profit *= self.exchange_rate
        return round(profit, 2)

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
        form.instance.fullfilled_by = self.request.user
        form.save()
        if form.instance.details_complete():
            if (
                form.instance.region.auto_close
                or "collection_booked" in self.request.POST
            ):
                self.close_order()
        return return_value

    def get_success_url(self):
        """Redirect to the order list."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"FBA order fulfilled for product {self.object.product_SKU}.",
        )
        return self.object.get_fulfillment_url()

    def close_order(self):
        """Complete and close the order."""
        self.object.close()
        if self.object.region.auto_close is True:
            self.object.update_stock_level()


class FBAOrderPrintout(FBAUserMixin, TemplateView):
    """View for FBA order printouts."""

    template_name = "fba/order_printout.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(models.FBAOrder, pk=self.kwargs.get("pk"))
        context["order"] = order
        bays = CCAPI.get_bays_for_product(order.product_ID)
        context["locations"] = [bay.name for bay in bays]
        context["selling_price"] = "{:.2f}".format(
            order.selling_price / 100,
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
