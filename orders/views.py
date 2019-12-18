"""Views for the Orders app."""
from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic.base import TemplateView

from home.models import CloudCommerceUser


class PackCountMonitor(TemplateView):
    """View for pack count display."""

    template_name = "print_audit/pack_count_monitor.html"

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
