"""View for Product Range page."""

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

from inventory import forms, models

from .views import InventoryUserMixin


class ProductRangeView(InventoryUserMixin, TemplateView):
    """Product Range page view."""

    template_name = "inventory/product_range/product_range.html"
    form_class = forms.ProductRangeForm

    def get(self, *args, **kwargs):
        """Process HTTP request."""
        self.get_range()
        if self.product_range is None or self.product_range.id == 0:
            return self.range_error()
        return super().get(*args, **kwargs)

    def get_range(self):
        """Get product range details from Cloud Commerce."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )

    def get_initial(self):
        """Get initial data for form."""
        initial = super().get_initial()
        initial["end_of_line"] = self.product_range.end_of_line
        return initial

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        if form.cleaned_data["end_of_line"] != self.product_range.end_of_line:
            self.product_range.set_end_of_line(form.cleaned_data["end_of_line"])
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:product_range", kwargs={"range_pk": self.product_range.pk}
        )

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["product_range"] = self.product_range
        context_data["products"] = self.product_range.products.all()
        return context_data

    def range_error(self):
        """Show error page."""
        return RangeError.as_view()(self.request)


class RangeError(TemplateView):
    """View for Product Range not found error page."""

    template_name = "inventory/product_range_404.html"

    def get(self, request, *args, **kwargs):
        """Return rendered response with 404 error code."""
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=404)
