"""Views for the Orders app."""
from django.db.models import Count, Q
from django.shortcuts import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from home.models import CloudCommerceUser
from home.views import UserInGroupMixin
from orders import models


class OrdersUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the print audit group."""

    groups = ["orders"]


class Index(OrdersUserMixin, TemplateView):
    """Main view for the orders app."""

    template_name = "orders/index.html"


class BreakageIndex(OrdersUserMixin, TemplateView):
    """Main view for breakages."""

    template_name = "orders/breakages.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        context["breakages"] = models.Breakage.objects.all()
        return context


class AddBreakage(OrdersUserMixin, CreateView):
    """View for creating new Breakage objects."""

    model = models.Breakage
    fields = ["product_sku", "order_id", "note", "packer"]

    def get_success_url(self):
        """Return URL to redirect to after succesfull form submission."""
        return reverse("orders:breakages")


class UpdateBreakage(OrdersUserMixin, UpdateView):
    """View for updating Breakage objects."""

    model = models.Breakage
    fields = ["product_sku", "order_id", "note", "packer"]

    def get_object(self, queryset=None):
        """Return object to update."""
        return models.Breakage.objects.get(id=self.kwargs["breakage_id"])

    def get_success_url(self):
        """Return URL to redirect to after succesfull form submission."""
        return reverse("orders:breakages")


class DeleteBreakage(OrdersUserMixin, DeleteView):
    """View for deleting Breakage objects."""

    model = models.Breakage

    def get_object(self, queryset=None):
        """Return object to delete."""
        return models.Breakage.objects.get(id=self.kwargs["breakage_id"])

    def get_success_url(self):
        """Return URL to redirect to after succesfull form submission."""
        return reverse("orders:breakages")


class PackCountMonitor(TemplateView):
    """View for pack count display."""

    template_name = "orders/pack_count_monitor.html"

    def get_context_data(self, *args, **kwargs):
        """Return HttpResponse with pack count data."""
        context = super().get_context_data(*args, **kwargs)
        date = timezone.now()
        qs = (
            CloudCommerceUser.unhidden.annotate(
                pack_count=Count(
                    "packingrecord",
                    filter=Q(
                        packingrecord__order__dispatched_at__year=date.year,
                        packingrecord__order__dispatched_at__month=date.month,
                        packingrecord__order__dispatched_at__day=date.day,
                    ),
                )
            )
            .filter(pack_count__gt=0)
            .order_by("-pack_count")
        )
        pack_count = [[_.full_name(), _.pack_count] for _ in qs]
        context["pack_counts"] = pack_count
        return context
