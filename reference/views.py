"""Views for the reference app."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class Index(LoginRequiredMixin, TemplateView):
    """View for the reference landing page."""

    template_name = 'reference/index.html'


class ReStructuredTextView(TemplateView):
    """Base View for rendered ReST files."""

    rst_file = None
    template_name = 'reference/rst_base.html'

    def get_context_data(self, *args, **kwargs):
        """Add ReST file to context."""
        context = super().get_context_data(*args, **kwargs)
        context['rst_file'] = self.rst_file
        return context


class ProductCreation(LoginRequiredMixin, ReStructuredTextView):
    """View for product creation documentation."""

    rst_file = 'reference/product_creation.rst'


class PackageTypes(LoginRequiredMixin, ReStructuredTextView):
    """View for explaination of package types."""

    rst_file = 'reference/package_types.rst'


class InventoryReference(LoginRequiredMixin, ReStructuredTextView):
    """View for inventory documentation."""

    rst_file = 'reference/inventory_reference.rst'
