"""Views for breakages."""

from django.shortcuts import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from print_audit import models

from .views import PrintAuditUserMixin


class BreakageIndex(PrintAuditUserMixin, TemplateView):
    """Main view for breakages."""

    template_name = "print_audit/breakages_index.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        context["breakages"] = models.Breakage.objects.all()
        return context


class AddBreakage(PrintAuditUserMixin, CreateView):
    """View for creating new Breakage objects."""

    model = models.Breakage
    fields = ["product_sku", "order_id", "note", "packer"]

    def get_success_url(self):
        """Return URL to redirect to after succesfull form submission."""
        return reverse("print_audit:breakages")


class UpdateBreakage(PrintAuditUserMixin, UpdateView):
    """View for updating Breakage objects."""

    model = models.Breakage
    fields = ["product_sku", "order_id", "note", "packer"]

    def get_object(self, queryset=None):
        """Return object to update."""
        return models.Breakage.objects.get(id=self.kwargs["breakage_id"])

    def get_success_url(self):
        """Return URL to redirect to after succesfull form submission."""
        return reverse("print_audit:breakages")


class DeleteBreakage(PrintAuditUserMixin, DeleteView):
    """View for deleting Breakage objects."""

    model = models.Breakage

    def get_object(self, queryset=None):
        """Return object to delete."""
        return models.Breakage.objects.get(id=self.kwargs["breakage_id"])

    def get_success_url(self):
        """Return URL to redirect to after succesfull form submission."""
        return reverse("print_audit:breakages")
