"""DescriptionsView class."""

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView

from inventory import forms, models

from .views import InventoryUserMixin


class DescriptionsView(InventoryUserMixin, UpdateView):
    """View for CreateRangeForm."""

    model = models.ProductRange
    form_class = forms.EditRangeForm
    template_name = "inventory/product_range/descriptions.html"

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        messages.add_message(self.request, messages.SUCCESS, "Description Updated")
        self.range_pk = form.instance.pk
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:descriptions", kwargs={"pk": self.range_pk})

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        form = context_data["form"]
        context_data["product_range"] = form.instance
        return context_data
