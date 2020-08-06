"""Views for the FBA app."""

import cc_products
from django.contrib import messages
from django.shortcuts import reverse
from django.views.generic import ListView, TemplateView
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
        product = cc_products.get_product(product_ID)
        initial["product_SKU"] = product.sku
        initial["product_ID"] = product_ID
        initial["product_name"] = product.full_name
        return initial

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
