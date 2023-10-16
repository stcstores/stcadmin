"""Views for managing suppliers."""

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    RedirectView,
    TemplateView,
    UpdateView,
)

from inventory import forms, models

from .views import InventoryUserMixin


class Suppliers(InventoryUserMixin, TemplateView):
    """View for the list of suppliers."""

    template_name = "inventory/suppliers/suppliers.html"

    def get_context_data(self, *args, **kwargs):
        """Add suppliers to the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["active_suppliers"] = models.Supplier.objects.active()
        context["inactive_suppliers"] = models.Supplier.objects.inactive()
        context["blacklisted_suppliers"] = models.Supplier.objects.blacklisted()
        return context


class Supplier(InventoryUserMixin, TemplateView):
    """View for supplier details."""

    template_name = "inventory/suppliers/supplier.html"

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
    template_name = "inventory/suppliers/supplier_form.html"


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
    template_name = "inventory/suppliers/suppliercontact_form.html"

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
    template_name = "inventory/suppliers/suppliercontact_form.html"

    def get_context_data(self, *args, **kwargs):
        """Add supplier to the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["supplier"] = context["form"].instance.supplier
        return context


class DeleteSupplierContact(InventoryUserMixin, DeleteView):
    """View for deleting supplier contacts."""

    model = models.SupplierContact
    template_name = "inventory/suppliers/suppliercontact_confirm_delete.html"

    def get_success_url(self):
        """Return the URL to redirect to after a successful deletion."""
        instance = get_object_or_404(models.SupplierContact, id=self.kwargs["pk"])
        return reverse_lazy("inventory:supplier", args=[instance.supplier.id])


class AddSupplierToBlacklist(FormView):
    """View for adding suppliers to the blacklist."""

    form_class = forms.AddSupplierToBlacklistForm
    template_name = "inventory/suppliers/add_blacklisted_supplier.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["suppliers"] = models.Supplier.objects.values_list("name", flat=True)
        return context

    def form_valid(self, form):
        """Save blacklisted supplier."""
        form.save()
        self.supplier = form.instance
        return super().form_valid(form)

    def get_success_url(self):
        """Return redirect url."""
        return self.supplier.get_absolute_url()


class RemoveBlacklistedSupplier(RedirectView):
    """View for removing suppliers from the blacklist."""

    def get_redirect_url(self, *args, **kwargs):
        """Remove supplier from blacklist and mark it as inactive."""
        supplier = get_object_or_404(models.Supplier, id=self.kwargs["pk"])
        supplier.active = False
        supplier.blacklisted = False
        supplier.save()
        return supplier.get_absolute_url()


class ActivateBlacklistedSupplier(RedirectView):
    """View for removing suppliers from the blacklist and reactivating them."""

    def get_redirect_url(self, *args, **kwargs):
        """Remove supplier from blacklist and mark it as active."""
        supplier = get_object_or_404(models.Supplier, id=self.kwargs["pk"])
        supplier.active = True
        supplier.blacklisted = False
        supplier.save()
        return supplier.get_absolute_url()


class BlacklistSupplier(InventoryUserMixin, RedirectView):
    """View to mark a supplier as blacklisted."""

    def get_redirect_url(self, *args, **kwargs):
        """Toggle the active status of a supplier."""
        supplier = get_object_or_404(models.Supplier, pk=kwargs["pk"])
        supplier.active = False
        supplier.blacklisted = True
        supplier.save()
        return supplier.get_absolute_url()
