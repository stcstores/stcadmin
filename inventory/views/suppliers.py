"""Views for managing suppliers."""

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from inventory import models

from .views import InventoryUserMixin


class Suppliers(InventoryUserMixin, TemplateView):
    """View for the list of suppliers."""

    template_name = "inventory/suppliers.html"

    def get_context_data(self, *args, **kwargs):
        """Add suppliers to the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["active_suppliers"] = models.Supplier.objects.active()
        context["inactive_suppliers"] = models.Supplier.objects.inactive()
        return context


class Supplier(InventoryUserMixin, TemplateView):
    """View for supplier details."""

    template_name = "inventory/supplier.html"

    def get_context_data(self, *args, **kwargs):
        """Add supplier to the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["supplier"] = get_object_or_404(models.Supplier, id=self.kwargs["pk"])
        context["contacts"] = context["supplier"].supplier_contacts.all()
        return context


class CreateSupplier(InventoryUserMixin, CreateView):
    """View for creating suppliers."""

    model = models.Supplier
    fields = ["name"]


class ToggleSupplierActive(InventoryUserMixin, RedirectView):
    """View to toggle the activation status of a supplier."""

    def get_redirect_url(self, *args, **kwargs):
        """Toggle the active status of a supplier."""
        supplier = get_object_or_404(models.Supplier, pk=kwargs["pk"])
        supplier.active = not supplier.active
        supplier.save()
        return supplier.get_absolute_url()


class CreateSupplierContact(InventoryUserMixin, CreateView):
    """View for creating supplier contacts."""

    model = models.SupplierContact
    fields = ["name", "phone", "email", "notes"]

    def form_valid(self, form):
        """Add the supplier to the contact object."""
        self.object = form.save(commit=False)
        self.object.supplier = get_object_or_404(
            models.Supplier, pk=self.kwargs["supplier_pk"]
        )
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        """Add supplier to the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["supplier"] = get_object_or_404(
            models.Supplier, pk=self.kwargs["supplier_pk"]
        )
        return context


class UpdateSupplierContact(InventoryUserMixin, UpdateView):
    """View for updating supplier contacts."""

    model = models.SupplierContact
    fields = ["name", "phone", "email", "notes"]

    def get_context_data(self, *args, **kwargs):
        """Add supplier to the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["supplier"] = context["form"].instance.supplier
        return context


class DeleteSupplierContact(InventoryUserMixin, DeleteView):
    """View for deleting supplier contacts."""

    model = models.SupplierContact

    def get_success_url(self):
        """Return the URL to redirect to after a successful deletion."""
        instance = get_object_or_404(models.SupplierContact, id=self.kwargs["pk"])
        return reverse_lazy("inventory:supplier", args=[instance.supplier.id])
