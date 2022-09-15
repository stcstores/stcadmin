"""Views for the channels app."""

from collections import defaultdict

from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
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


class ShopifyListing(ChannelsUserMixin, TemplateView):
    """View for Shopify listings."""

    template_name = "channels/shopify/shopify_listing.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["listing"] = get_object_or_404(
            models.shopify_models.ShopifyListing, pk=self.kwargs.get("listing_pk")
        )
        context["product_range"] = context["listing"].product_range
        return context


class CreateShopifyListing(ChannelsUserMixin, CreateView):
    """Create a new Shopify listing."""

    model = models.shopify_models.ShopifyListing
    form_class = forms.ShopifyListingForm
    template_name = "channels/shopify/shopify_listing_form.html"

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

    def get_success_url(self):
        """Redirect to the edit listing page for the listing."""
        return reverse_lazy(
            "channels:update_shopify_tags", kwargs={"pk": self.object.pk}
        )


class UpdateShopifyListing(ChannelsUserMixin, UpdateView):
    """Update a Shopify listing."""

    model = models.shopify_models.ShopifyListing
    form_class = forms.ShopifyListingForm
    template_name = "channels/shopify/shopify_listing_form.html"

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
        return HttpResponseRedirect(self.get_success_url())

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

    def get_success_url(self):
        """Return redirect URL."""
        return reverse_lazy(
            "channels:update_shopify_collections", kwargs={"pk": self.object.pk}
        )


class UpdateShopifyTags(ChannelsUserMixin, UpdateView):
    """View for setting Shopify tags."""

    model = models.shopify_models.ShopifyListing
    form_class = forms.ShopifyTagsForm
    template_name = "channels/shopify/shopify_tags_form.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["listing"] = self.object
        context["listing_tags"] = context["listing"].tags.all()
        all_tags = models.shopify_models.ShopifyTag.objects.all()
        tag_groups = defaultdict(list)
        for tag in all_tags:
            tag_groups[tag.name[0]].append(tag)
        context["tag_groups"] = dict(tag_groups)
        return context

    def get_success_url(self):
        """Return redirect URL."""
        if "create_tag" in self.request.POST:
            return reverse_lazy(
                "channels:create_shopify_tag", kwargs={"listing_pk": self.object.id}
            )
        return self.object.get_absolute_url()


class UpdateShopifyCollections(ChannelsUserMixin, UpdateView):
    """View for setting Shopify collections."""

    model = models.shopify_models.ShopifyListing
    form_class = forms.ShopifyCollectionsForm
    template_name = "channels/shopify/shopify_collections_form.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["listing"] = self.object
        context["listing_collections"] = context["listing"].collections.all()
        context[
            "all_collections"
        ] = models.shopify_models.ShopifyCollection.objects.all()
        return context

    def get_success_url(self):
        """Redirect to the listing's listing page."""
        return reverse_lazy(
            "channels:update_shopify_tags", kwargs={"pk": self.object.id}
        )


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


@method_decorator(csrf_exempt, name="dispatch")
class UploadShopifyListing(ChannelsUserMixin, View):
    """View to trigger updating or creating a Shopify listing."""

    def post(self, *args, **kwargs):
        """Trigger the creation or update of a Shopify listing."""
        listing_pk = self.request.POST["listing_pk"]
        listing = get_object_or_404(models.shopify_models.ShopifyListing, pk=listing_pk)
        listing.upload()
        return HttpResponse("ok")


class ShopifyListingStatus(ChannelsUserMixin, TemplateView):
    """View for displaying the current status of a Shopify listing."""

    template_name = "channels/shopify/shopify_listing_status.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        listing = get_object_or_404(
            models.shopify_models.ShopifyListing, pk=self.kwargs["listing_pk"]
        )
        try:
            update = listing.get_last_update()
        except models.shopify_models.ShopifyUpdate.DoesNotExist:
            context["ongoing"] = False
        else:
            context["update"] = update
            if update.completed_at is None:
                context["ongoing"] = True
            else:
                context["ongoing"] = False
        if listing.product_id is None:
            context["uploaded"] = False
            context["active"] = False
        else:
            context["uploaded"] = True
            context["active"] = listing.listing_is_active()
        return context


@method_decorator(csrf_exempt, name="dispatch")
class ShopifyListingActiveStatus(ChannelsUserMixin, View):
    """View for getting the active status of a Shopify listing."""

    def post(self, *args, **kwargs):
        """Return the status of a listing as JSON."""
        listing_id = self.request.POST["listing_id"]
        listing = get_object_or_404(models.shopify_models.ShopifyListing, id=listing_id)
        active_status = listing.listing_is_active()
        return JsonResponse({"listing_id": listing.id, "active": active_status})


class ShopifyTagList(ChannelsUserMixin, TemplateView):
    """View for showing a list of Shopify tags."""

    template_name = "channels/shopify/shopify_tag_list.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["tags"] = models.shopify_models.ShopifyTag.objects.all()
        return context


class CreateShopifyTag(CreateView):
    """View for creating new Shopify tags."""

    model = models.shopify_models.ShopifyTag
    form_class = forms.ShopifyTagForm
    template_name = "channels/shopify/create_shopify_tag.html"

    def get_success_url(self):
        """Redirect back to the update tag page if applicable."""
        listing_pk = self.kwargs.get("listing_pk")
        if listing_pk is None:
            return reverse_lazy("channels:create_shopify_tag")
        else:
            listing = get_object_or_404(
                models.shopify_models.ShopifyListing, pk=listing_pk
            )
            listing.tags.add(self.object)
            return reverse_lazy(
                "channels:update_shopify_tags", kwargs={"pk": listing.pk}
            )
