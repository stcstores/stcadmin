"""Views for the channels app."""


from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from channels import forms, models
from home.views import UserInGroupMixin
from inventory.models import ProductRange


class ChannelsUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the channels group."""

    groups = ["channels"]


class Index(ChannelsUserMixin, TemplateView):
    """Main view for the orders app."""

    template_name = "channels/index.html"


class CreateShopifyListing(CreateView):
    """Create a new Shopify listing."""

    model = models.shopify_models.ShopifyListing
    form_class = forms.ShopifyListingForm
    template_name = "channels/shopify/shopify_listing.html"

    def post(self, request, *args, **kwargs):
        """Process a form submission."""
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = forms.VariationFormset(self.request.POST)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        """Create a Shopify listing from the form data."""
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        return super().form_valid(form)

    def form_invalid(self, form, formset):
        """Return the rendered template with form errors."""
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def get_initial(self):
        """Return initial data for the form."""
        initial = super().get_initial()
        self.product_range = get_object_or_404(
            ProductRange, pk=self.kwargs["product_range_pk"]
        )
        initial["product_range"] = self.product_range
        initial["title"] = self.product_range.name
        initial["description"] = self.product_range.description
        return initial

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        products = self.product_range.products.variations()
        context["formset"] = kwargs.get(
            "formset",
            inlineformset_factory(
                models.shopify_models.ShopifyListing,
                models.shopify_models.ShopifyVariation,
                form=forms.ShopifyVariationForm,
                extra=len(products),
                can_delete=False,
            )(initial=[{"product": product} for product in products]),
        )
        return context


class UpdateShopifyListing(UpdateView):
    """Update a Shopify listing."""

    model = models.shopify_models.ShopifyListing
    form_class = forms.ShopifyListingForm
    template_name = "channels/shopify/shopify_listing.html"

    def post(self, *args, **kwargs):
        """Process a form submission."""
        self.object = self.get_object()
        form = self.get_form()
        formset = forms.VariationFormset(
            self.request.POST,
            instance=self.object,
        )
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        """Save changes according to form data."""
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        return super().form_valid(form)

    def form_invalid(self, form, formset):
        """Return a rendered template with form errors."""
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["formset"] = kwargs.get(
            "formset",
            inlineformset_factory(
                models.shopify_models.ShopifyListing,
                models.shopify_models.ShopifyVariation,
                form=forms.ShopifyVariationForm,
                extra=0,
                can_delete=False,
            )(instance=self.object),
        )
        return context


class ShopifyProducts(ChannelsUserMixin, ListView):
    """View for product search page."""

    template_name = "channels/shopify/search_page.html"
    form_class = forms.ProductSearchForm
    model = ProductRange
    paginate_by = 50

    def get_queryset(self):
        """Return a queryset of product ranges filtered by the request's GET params."""
        form = self.form_class(self.request.GET)
        form.is_valid()
        form.save()
        return form.ranges

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(self.request.GET)
        return context
