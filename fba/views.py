"""Views for the FBA app."""

import cc_products
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView, View
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
            return JsonResponse(response)
        except Exception as e:
            print(e)
            return HttpResponseBadRequest()

    def parse_request(self):
        """Get request parameters from POST."""
        post_data = self.request.POST
        self.selling_price = float(post_data.get("selling_price"))
        self.quantity = int(post_data.get("quantity"))
        self.country_id = int(post_data.get("country"))
        self.purchase_price = float(post_data.get("purchase_price"))
        self.fba_fee = float(post_data.get("fba_fee"))
        country_id = int(post_data.get("country"))
        self.country = models.FBACountry.objects.get(id=country_id)
        self.exchange_rate = float(self.country.country.currency.exchange_rate)

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
            vat = self.selling_price * 0.2
            vat = round(vat, 2)
        else:
            vat = 0.0
        return vat

    def get_postage_to_fba(self):
        """Return the caclulated price to post to FBA."""
        postage_to_fba = float(self.country.postage_price) / 100.0
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
