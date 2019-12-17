"""Views the Monitor app."""

import json

from django.db.models import Count, F, Q
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic.base import TemplateView

from feedback import models
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


class FeedbackMonitor(TemplateView):
    """View for feedback display."""

    template_name = "monitor/feedback.html"

    def get_feedback(self):
        """Return feedback data."""
        date = timezone.now()
        feedback = (
            models.UserFeedback.objects.filter(user__hidden=False)
            .annotate(cc_user_id=F("user__pk"), feedback_id=F("feedback_type__pk"))
            .values("cc_user_id", "feedback_id")
            .annotate(
                count=Count(
                    "pk",
                    filter=Q(timestamp__year=date.year, timestamp__month=date.month),
                )
            )
            .filter(count__gt=0)
            .order_by("cc_user_id", "feedback_id")
        )
        return feedback

    def get_users(self):
        """Return a list of users with feedback data."""
        feedback_types = {_.id: _ for _ in models.Feedback.objects.all()}
        feedback = self.get_feedback()
        users = list(CloudCommerceUser.unhidden.all())
        for user in users:
            user.score = 0
            user.feedback = []
            for record in feedback:
                if record["cc_user_id"] == user.id:
                    feedback_type = feedback_types[record["feedback_id"]]
                    count = record["count"]
                    user.score += feedback_type.score * count
                    user.feedback.append((feedback_type, range(count)))
            user.feedback = sorted(
                user.feedback, key=lambda x: x[0].score, reverse=True
            )
        users = sorted(
            [user for user in users if user.feedback],
            key=lambda x: x.score,
            reverse=True,
        )
        return users

    def get_context_data(self, *args, **kwargs):
        """Return HttpResponse with feedback data for current month."""
        context = super().get_context_data(*args, **kwargs)
        users = self.get_users()
        context["users"] = users
        context["total"] = sum((user.score for user in users))
        return context
