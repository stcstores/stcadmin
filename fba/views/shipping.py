"""Views for managing FBA shipments."""

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, View
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from fba import forms, models

from .fba import FBAUserMixin


class Shipments(FBAUserMixin, TemplateView):
    """View for managing current shipments."""

    template_name = "fba/shipments/shipments.html"

    def get_context_data(self, **kwargs):
        """Return context data for the template."""
        context = super().get_context_data(**kwargs)
        context["previous_exports"] = models.FBAShipmentExport.objects.all()[:50]
        unexported_shipments = models.FBAShipmentOrder.objects.filter(
            export__isnull=True
        )
        context["current_shipments"] = unexported_shipments.filter(is_on_hold=False)
        context["held_shipments"] = unexported_shipments.filter(is_on_hold=True)
        return context


class ShipmentDestinations(FBAUserMixin, TemplateView):
    """View for managing shipment destinations."""

    template_name = "fba/shipments/destinations.html"

    def get_context_data(self, **kwargs):
        """Return context data for the template."""
        context = super().get_context_data(**kwargs)
        context["destinations"] = models.FBAShipmentDestination.objects.filter(
            is_enabled=True
        )
        return context


class BaseDestinationFormView:
    """Base view for destination forms."""

    model = models.FBAShipmentDestination
    template_name = "fba/shipments/shipment_destination_form.html"
    form_class = forms.ShipmentDestinationForm
    success_url = reverse_lazy("fba:shipment_destinations")


class CreateDestination(BaseDestinationFormView, FBAUserMixin, CreateView):
    """View for creating shipment destinations."""

    pass


class UpdateDestination(BaseDestinationFormView, FBAUserMixin, UpdateView):
    """View for updating shipment destinations."""

    pass


class DisableDestination(FBAUserMixin, RedirectView):
    """View for marking destinations as disabled."""

    def get_redirect_url(self, *args, **kwargs):
        """Mark a shipment destination as disabled."""
        destination = get_object_or_404(
            models.FBAShipmentDestination, pk=self.kwargs.get("pk")
        )
        destination.is_enabled = False
        destination.save()
        return reverse_lazy("fba:shipment_destinations")


class CreateFBAShipmentFile(FBAUserMixin, RedirectView):
    """View for closing shipment orders."""

    def get_redirect_url(self, *args, **kwargs):
        """Close a shipment order."""
        shipment = get_object_or_404(
            models.FBAShipmentOrder, pk=self.kwargs["fba_order_pk"]
        )
        shipment.close_shipment_order()
        return reverse_lazy("fba:shipments")


class DownloadFBAShipmentFile(FBAUserMixin, View):
    """View for generating FBA Shipment files."""

    def get(self, *args, **kwargs):
        """Return an ITD shipment file download."""
        export = get_object_or_404(models.FBAShipmentExport, pk=self.kwargs["pk"])
        contents = export.generate_export_file()
        response = HttpResponse(contents, content_type="text/csv")
        filename = f"FBA_Shipment_File_{export.created_at.strftime('%Y-%m-%d')}.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class DownloadUPSAddressFile(FBAUserMixin, RedirectView):
    """View for generating FBA UPS address files."""

    def get(self, *args, **kwargs):
        """Return an ITD shipment file download."""
        export = get_object_or_404(models.FBAShipmentExport, pk=self.kwargs["pk"])
        contents = export.generate_address_file()
        response = HttpResponse(contents, content_type="text/csv")
        filename = "FBA_Shipment_ADDRESS.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class CreateShipment_SelectDestination(FBAUserMixin, TemplateView):
    """View for selecting destinations for new shipments."""

    template_name = "fba/shipments/create_shipment/select_destination.html"

    def get_context_data(self, **kwargs):
        """Return context data for the template."""
        context = super().get_context_data(**kwargs)
        context["destinations"] = models.FBAShipmentDestination.objects.filter(
            is_enabled=True
        )
        return context


class CreateShipment_CreateDestination(CreateDestination):
    """View to create a new shipment destination for a new shipment."""

    template_name = "fba/shipments/create_shipment/create_destination.html"

    def get_success_url(self, *args, **kwargs):
        """Redirect to the create shipment page."""
        return reverse_lazy(
            "fba:create_shipment",
            kwargs={"destination_pk": self.object.pk},
        )


class CreateShipment(FBAUserMixin, RedirectView):
    """View for creating FBA Shipment orders."""

    def get_redirect_url(self, *args, **kwargs):
        """Return URL to redirect to after a succesful creation."""
        destination = get_object_or_404(
            models.FBAShipmentDestination, pk=self.kwargs["destination_pk"]
        )
        shipment_method = models.FBAShipmentMethod.objects.first()
        shipment = models.FBAShipmentOrder.objects.create(
            destination=destination,
            shipment_method=shipment_method,
            user=self.request.user,
        )
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Shipment {shipment.order_number} created.",
        )
        return reverse_lazy("fba:update_shipment", kwargs={"pk": shipment.pk})


class UpdateShipment(FBAUserMixin, UpdateView):
    """View for updating FBA Shipment orders."""

    model = models.FBAShipmentOrder
    template_name = "fba/shipments/create_shipment/update_shipment.html"
    form_class = forms.ShipmentOrderForm

    def get_success_url(self):
        """Return URL to redirect to after a succesful update."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Shipment {self.object.order_number} updated.",
        )
        if "new_package" in self.request.POST:
            return reverse_lazy(
                "fba:create_package", kwargs={"order_pk": self.object.pk}
            )
        elif "edit_package" in self.request.POST:
            package_id = self.request.POST["edit_package"]
            return reverse_lazy("fba:update_package", kwargs={"pk": package_id})
        elif "delete_package" in self.request.POST:
            package_id = self.request.POST["delete_package"]
            return reverse_lazy("fba:delete_package", kwargs={"pk": package_id})
        return reverse_lazy("fba:update_shipment", args=[self.object.pk])


class BasePackageFormView:
    """Base view for package form pages."""

    model = models.FBAShipmentPackage
    template_name = "fba/shipments/create_shipment/package_form.html"
    form_class = forms.PackageForm

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["item_formset"] = self.get_item_formset()
        return context

    def form_valid(self, form):
        """Save shipment and packages if the form is valid."""
        item_formset = self.get_item_formset()
        if not item_formset.is_valid():
            return self.form_invalid(form)
        with transaction.atomic():
            self.object = form.save()
            item_formset.instance = self.object
            item_formset.save()
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        """Redirect to the update shipment page."""
        self.set_message()
        return reverse_lazy(
            "fba:update_shipment", kwargs={"pk": self.object.shipment_order.pk}
        )


class CreatePackage(BasePackageFormView, FBAUserMixin, CreateView):
    """View for creating packages and items."""

    def get_initial(self, *args, **kwargs):
        """Set the package's shipment."""
        initial = super().get_initial(*args, **kwargs)
        initial["shipment_order"] = get_object_or_404(
            models.FBAShipmentOrder, pk=self.kwargs["order_pk"]
        )
        return initial

    def set_message(self):
        """Create a success message."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            (
                f"Package {self.object.package_number} added to "
                f"Shipment {self.object.shipment_order.order_number}."
            ),
        )

    def get_item_formset(self):
        """Return a formset for packages."""
        if self.request.POST:
            formset = forms.ItemFormset(self.request.POST)
        else:
            formset = forms.ItemFormset()
        return formset


class UpdatePackage(BasePackageFormView, FBAUserMixin, UpdateView):
    """View for updating packages and items."""

    def set_message(self):
        """Create a success message."""
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Shipment Order {self.object.shipment_order.order_number} updated.",
        )

    def get_item_formset(self):
        """Return a formset for packages."""
        if self.request.POST:
            formset = forms.ItemFormset(self.request.POST, instance=self.object)
        else:
            formset = forms.ItemFormset(
                instance=self.object, queryset=self.object.shipment_item.all()
            )
        return formset


class ToggleShipmentHeld(FBAUserMixin, RedirectView):
    """View to toggle the is_on_hold attribue of shipments."""

    def get_redirect_url(self, *args, **kwargs):
        """Toggle is_on_hold and redirect to shipments."""
        shipment = get_object_or_404(models.FBAShipmentOrder, pk=self.kwargs["pk"])
        shipment.is_on_hold = not shipment.is_on_hold
        shipment.save()
        return reverse_lazy("fba:shipments")


class DeleteShipment(FBAUserMixin, DeleteView):
    """View for deleting shipments."""

    template_name = "fba/shipments/confirm_delete_shipment.html"
    model = models.FBAShipmentOrder
    success_url = reverse_lazy("fba:shipments")


class DeletePackage(FBAUserMixin, DeleteView):
    """View for deleting packages."""

    template_name = "fba/shipments/confirm_delete_package.html"
    model = models.FBAShipmentPackage

    def get_success_url(self):
        """Redirect to the deleted package's shipment order."""
        return reverse_lazy(
            "fba:update_shipment", kwargs={"pk": self.object.shipment_order.pk}
        )


class HistoricShipments(FBAUserMixin, ListView):
    """Display a filterable list of orders."""

    template_name = "fba/shipments/historic_shipments.html"
    model = models.FBAShipmentExport
    paginate_by = 50
    orphans = 3
    form_class = forms.FBAShipmentFilter

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
