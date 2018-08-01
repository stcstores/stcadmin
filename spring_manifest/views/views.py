"""Views for manifest app."""

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from home.views import UserInGroupMixin
from spring_manifest import forms, models


class SpringUserMixin(UserInGroupMixin):
    """View mixin ensuring user has permissions for this app."""

    groups = ["manifests"]


class Index(SpringUserMixin, TemplateView):
    """View for manifest index page."""

    template_name = "spring_manifest/index.html"


class UpdateOrderView(SpringUserMixin, FormView):
    """View for update order form."""

    form_class = forms.UpdateOrderForm
    fields = ("country", "product_count", "package_count", "manifest", "service")
    template_name = "spring_manifest/update_order.html"

    def get_form_kwargs(self, *args, **kwargs):
        """Return kwargs for form."""
        self.object = self.get_object()
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs["instance"] = self.object
        return form_kwargs

    def get_success_url(self):
        """Return URL to redirect to after order is updated."""
        if "split" in self.form.data:
            return reverse_lazy(
                "spring_manifest:split_order", kwargs={"order_pk": self.object.id}
            )
        if "return" in self.form.data:
            if self.object.manifest:
                return reverse_lazy(
                    "spring_manifest:manifest",
                    kwargs={"manifest_id": self.object.manifest_id},
                )
            return reverse_lazy("spring_manifest:canceled_orders")
        return reverse_lazy(
            "spring_manifest:update_order", kwargs={"order_pk": self.object.id}
        )

    def get_object(self):
        """Return order to be updated."""
        order = get_object_or_404(models.ManifestOrder, id=self.kwargs.get("order_pk"))
        if order.manifest is not None:
            self.manifest_id = order.manifest.id
        else:
            self.manifest_id = None
        return order

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data()
        context["order"] = self.object
        return context

    def form_valid(self, form):
        """Update database."""
        self.form = form
        form.save()
        if form.changed_data:
            messages.add_message(self.request, messages.SUCCESS, "Order Updated.")
        return super().form_valid(form)


class ManifestListView(SpringUserMixin, TemplateView):
    """View for list of manifests."""

    template_name = "spring_manifest/manifest_list.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        models.update_manifest_orders()
        context["current_manifests"] = models.Manifest.unfiled.all()
        context["previous_manifests"] = models.Manifest.filed.all()[:50]
        context["unmanifested_orders"] = models.ManifestOrder.unmanifested.all()
        return context


class ManifestView(SpringUserMixin, TemplateView):
    """View for manifests."""

    template_name = "spring_manifest/manifest.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        manifest_id = self.kwargs["manifest_id"]
        manifest = get_object_or_404(models.Manifest, id=manifest_id)
        if manifest.status == manifest.UNFILED:
            models.update_manifest_orders()
        orders = manifest.manifestorder_set.all().order_by("dispatch_date")
        context["manifest"] = manifest
        context["orders"] = orders
        context["services"] = {
            service.name: len([order for order in orders if order.service == service])
            for service in models.ManifestService.enabled_services.all()
        }
        return context


class CanceledOrdersView(SpringUserMixin, TemplateView):
    """View for canceled orders."""

    template_name = "spring_manifest/canceled_orders.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        context["unmanifested_orders"] = models.ManifestOrder.objects.filter(
            manifest__isnull=True, canceled=False
        )
        context["canceled_orders"] = models.ManifestOrder.canceled_orders.filter(
            manifest__isnull=True, canceled=True
        )
        return context


class SplitOrderView(SpringUserMixin, FormView):
    """View for splitting orders."""

    form_class = forms.PackageFormset
    template_name = "spring_manifest/split_order.html"

    def get_form_kwargs(self):
        """Return kwargs for form."""
        kwargs = super().get_form_kwargs()
        self.order = get_object_or_404(
            models.ManifestOrder, id=self.kwargs.get("order_pk")
        )
        kwargs["instance"] = self.order
        return kwargs

    def get_success_url(self):
        """Return URL to redirect to after order has been updated."""
        if "return_to_order" in self.form.data:
            return reverse_lazy(
                "spring_manifest:update_order", kwargs={"order_pk": self.order.id}
            )
        return reverse_lazy(
            "spring_manifest:split_order", kwargs={"order_pk": self.order.id}
        )

    def form_valid(self, form):
        """Update database."""
        self.form = form
        form.save()
        form.clear_empty_packages()
        if "add_package" in self.request.POST:
            form.add_package()
        if not self.order.check_items():
            messages.add_message(
                self.request, messages.WARNING, "Item Quantity Discrepency."
            )
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["order"] = self.order
        context_data["children_formset"] = context_data.pop("form")
        return context_data


class OrderExists(SpringUserMixin, View):
    """View to check if an order ID exists."""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """If order ID exists redirect to edit page for it."""
        order_id = self.request.POST.get("order_id")
        try:
            order = models.ManifestOrder.objects.get(order_id=order_id)
        except models.ManifestOrder.DoesNotExist:
            return HttpResponse("0")
        else:
            return HttpResponse(
                reverse_lazy(
                    "spring_manifest:update_order", kwargs={"order_pk": order.pk}
                )
            )
