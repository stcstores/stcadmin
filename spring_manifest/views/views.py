"""Views for manifest app."""

import os
import threading
import time

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.edit import FormView

from home.views import UserInGroupMixin
from spring_manifest import forms, models

from .file_manifest.securedmail import FileSecuredMailManifest, SecuredMailManifestFile


class SpringUserMixin(UserInGroupMixin):
    """View mixin ensuring user has permissions for this app."""

    groups = ["manifests"]


class ManifestListView(SpringUserMixin, TemplateView):
    """View for list of manifests."""

    template_name = "spring_manifest/manifest_list.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        context["current_manifests"] = models.Manifest.unfiled.all()
        context["previous_manifests"] = models.Manifest.filed.all()[:50]
        context["unmanifested_orders"] = models.ManifestOrder.unmanifested.all()
        context["update"] = models.get_manifest_update()
        return context


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
        return get_object_or_404(models.ManifestOrder, id=self.kwargs.get("order_pk"))

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data()
        context["order"] = self.object
        return context

    def form_valid(self, form):
        """Update database."""
        self.form = form
        form.save()
        messages.add_message(self.request, messages.SUCCESS, "Order Updated.")
        return super().form_valid(form)


class ManifestView(SpringUserMixin, TemplateView):
    """View for manifests."""

    template_name = "spring_manifest/manifest.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        manifest_id = self.kwargs["manifest_id"]
        manifest = get_object_or_404(models.Manifest, id=manifest_id)
        orders = manifest.manifestorder_set.all().order_by("dispatch_date")
        context["manifest"] = manifest
        context["orders"] = orders
        context["services"] = {
            service.name: len([order for order in orders if order.service == service])
            for service in models.ManifestService.enabled_services.all()
        }
        context["update"] = models.get_manifest_update()
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


class UpdateManifest(SpringUserMixin, RedirectView):
    """Trigger a manifest update and return to the previous page."""

    def post(self, *args, **kwargs):
        """Disallow POST requests."""
        return HttpResponseNotAllowed((("GET",)))

    def get_redirect_url(self, *args, **kwargs):
        """Redirect to the provided URL."""
        self.update_manifest()
        time.sleep(1)
        return self.request.GET.get("return")

    def update_manifest(self):
        """Trigger an update of the manifest orders."""
        t = threading.Thread(target=models.update_manifest_orders)
        t.setDaemon(True)
        t.start()


class SendSecuredMailManifest(SpringUserMixin, RedirectView):
    """Send the Secured Mail manifest files to Secured Mail."""

    def get(self, *args, **kwargs):
        """Disallow GET requests."""
        return HttpResponseNotAllowed((("POST",)))

    def post(self, *args, **kwargs):
        """Allow GET requests."""
        return super().get(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        """Email files and return redirect to the manifest page."""
        self.send_manifest_files()
        return reverse_lazy(
            "spring_manifest:manifest",
            kwargs={"manifest_id": self.request.POST.get("manifest_id")},
        )

    def send_manifest_files(self):
        """Send the Secured Mail manifest files to Secured Mail."""
        number_of_bags = self.request.POST.get("number_of_bags")
        manifest = models.Manifest.objects.get(id=self.request.POST.get("manifest_id"))
        SecuredMailManifestFile.add_bag_number(manifest, number_of_bags)
        manifest_email = EmailMessage(
            f"Seaton Trading Company Manifest {manifest}",
            "",
            "error_logging@stcstores.co.uk",
            [settings.SECURED_MAIL_MANIFEST_EMAIL_ADDRESS],
            reply_to=["info@stcstores.co.uk"],
            attachments=[
                (
                    os.path.basename(manifest.manifest_file.name),
                    manifest.manifest_file.open(mode="rb").read(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            ],
        )
        docket_email = EmailMessage(
            f"Seaton Trading Company Docket {manifest}",
            "",
            "error_logging@stcstores.co.uk",
            [settings.SECURED_MAIL_DOCKET_EMAIL_ADDRESS],
            attachments=[
                (
                    os.path.basename(manifest.docket_file.name),
                    manifest.docket_file.open(mode="rb").read(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            ],
        )
        manifest_email.send()
        docket_email.send()
        manifest.files_sent = True
        manifest.save()


class FileManifestView(SpringUserMixin, RedirectView):
    """File a manifest."""

    def post(self, *args, **kwargs):
        """Disallow POST requests."""
        return HttpResponseNotAllowed((("GET",)))

    @staticmethod
    def file_manifest(manifest):
        """File manifest using appropriate FileManifest class."""
        if manifest.manifest_type.name == "Secured Mail":
            FileSecuredMailManifest(manifest)
        else:
            raise Exception(
                "Unknown manifest type {} for manifest {}".format(
                    manifest.manifest_type, manifest.id
                )
            )

    def get_manifest(self):
        """Return requested manifest."""
        manifest_id = self.kwargs["manifest_id"]
        manifest = get_object_or_404(models.Manifest, pk=manifest_id)
        if manifest.status != manifest.FAILED and manifest.manifest_file:
            return None
        return manifest

    def process_manifest(self):
        """Set manifest as in progress and start thread to file it."""
        manifest = self.get_manifest()
        if manifest is not None:
            t = threading.Thread(target=self.file_manifest, args=[manifest])
            t.setDaemon(True)
            t.start()
            time.sleep(3)
        else:
            messages.add_message(
                self.request, messages.ERROR, "Manifest already filed."
            )

    def get_redirect_url(self, *args, **kwargs):
        """Return URL to redirect to after manifest process starts."""
        self.process_manifest()
        return reverse_lazy(
            "spring_manifest:manifest",
            kwargs={"manifest_id": self.kwargs["manifest_id"]},
        )
