"""Views for the purchases app."""

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView

from home.views import UserInGroupMixin
from inventory.models import BaseProduct
from purchases import forms


class PurchasesUserMixin(UserInGroupMixin):
    """Mixin to validate user in in purchases group."""

    groups = ["purchases", "purchase_manager"]


class PurchaseManagerUserMixin(UserInGroupMixin):
    """Mixin to validate user in in purchase_manager group."""

    groups = ["purchase_manager"]


class ProductSearch(PurchasesUserMixin, TemplateView):
    """View for searching for products to purchase."""

    template_name = "purchases/product_search.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = forms.ProductSearchForm()
        return context


class ProductSearchResults(PurchasesUserMixin, ListView):
    """AJAX view for displaying product search results."""

    model = BaseProduct
    paginate_by = 50
    template_name = "purchases/product_search_results.html"

    def get_queryset(self):
        """Return product queryset."""
        form = forms.ProductSearchForm(self.request.GET)
        return form.get_queryset()


class CreatePurchase(PurchasesUserMixin, FormView):
    """View for creating new purchases."""

    form_class = forms.CreatePurchaseForm
    template_name = "purchases/create_purchase.html"
    success_url = reverse_lazy("purchases:product_search")

    def get_initial(self):
        """Return initial values for the form."""
        initial = super().get_initial()
        initial["product_id"] = self.kwargs["product_pk"]
        initial["purchaser"] = self.request.user.staff_member.id
        return initial

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["product"] = get_object_or_404(
            BaseProduct, pk=self.kwargs["product_pk"]
        )
        return context

    def form_valid(self, form):
        """Create a new purchase."""
        form.save()
        return super().form_valid(form)
