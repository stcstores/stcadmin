"""Views for display monitor."""

import json

from django.http import HttpResponse
from django.utils.timezone import now
from django.views import View
from django.views.generic.base import TemplateView
from print_audit import models


class DisplayMonitor(TemplateView):
    """View for display monitor."""

    template_name = "print_audit/display_monitor.html"


class PackCountMonitor(View):
    """View for pack count display."""

    def get(self, request):
        """Return HttpResponse with pack count data."""
        orders = models.CloudCommerceOrder.objects.filter(
            date_created__year=now().year,
            date_created__month=now().month,
            date_created__day=now().day,
        )
        packers = models.CloudCommerceUser.unhidden.all()
        pack_count = [
            (user.full_name(), orders.filter(user=user).count()) for user in packers
        ]
        pack_count = [count for count in pack_count if count[1] > 0]
        pack_count.sort(key=lambda x: x[1], reverse=True)
        return HttpResponse(json.dumps(pack_count))


class FeedbackMonitor(View):
    """View for feedback display."""

    def get(self, request):
        """Return HttpResponse with feedback data for current month."""
        all_feedback = models.UserFeedback.this_month.all()
        users = list(set([f.user for f in all_feedback if not f.user.hidden]))
        data = []
        for user in users:
            user_data = {
                "name": user.full_name(),
                "feedback": [],
                "score": models.UserFeedback.this_month.filter(user=user).score(),
            }
            feedback = [f for f in all_feedback if f.user == user]
            feedback_types = list(set([f.feedback_type for f in feedback]))
            for f_type in feedback_types:
                feedback_ids = [fb.id for fb in feedback if fb.feedback_type == f_type]
                user_data["feedback"].append(
                    {
                        "name": f_type.name,
                        "image_url": f_type.image.url,
                        "ids": feedback_ids,
                        "score": f_type.score,
                    }
                )
            data.append(user_data)
        data.sort(key=lambda x: x["score"], reverse=True)
        response = {"total": models.UserFeedback.this_month.all().score(), "data": data}
        return HttpResponse(json.dumps(response))
