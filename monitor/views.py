"""Views the Monitor app."""

import json

from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic.base import TemplateView

from home.models import CloudCommerceUser


class DisplayMonitor(TemplateView):
    """View for display monitor."""

    template_name = "monitor/monitor.html"


class PackCountMonitor(View):
    """View for pack count display."""

    def get(self, request):
        """Return HttpResponse with pack count data."""
        date = timezone.now()
        qs = (
            CloudCommerceUser.unhidden.annotate(
                pack_count=Count(
                    "cloudcommerceorder",
                    filter=Q(
                        cloudcommerceorder__date_created__year=date.year,
                        cloudcommerceorder__date_created__month=date.month,
                        cloudcommerceorder__date_created__day=date.day,
                    ),
                )
            )
            .filter(pack_count__gt=0)
            .order_by("-pack_count")
        )
        pack_count = [[_.full_name(), _.pack_count] for _ in qs]
        return HttpResponse(json.dumps(pack_count))
