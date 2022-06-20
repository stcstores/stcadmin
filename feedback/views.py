"""Views for the Feedback app."""
import datetime

from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, F, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from feedback import forms, models
from home.models import Staff
from home.views import UserInGroupMixin, UserLoginMixin


class FeedbackUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the feedback group."""

    groups = ["feedback"]


class FeedbackQuickview(UserLoginMixin, TemplateView):
    """View for feedback quickview page."""

    template_name = "feedback/feedback_quickview.html"


class UserFeedback(FeedbackUserMixin, TemplateView):
    """View for user feedback page."""

    template_name = "feedback/user_feedback.html"
    form_class = forms.FeedbackDateFilterForm

    def get(self, *args, **kwargs):
        """Create feedback date filter form."""
        self.form = self.form_class(
            self.request.GET.copy(),
            initial={self.form_class.DATES: self.form_class.ALL},
        )
        self.form.is_valid()
        return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        date_from = self.form.cleaned_data[self.form.DATE_FROM]
        date_to = self.form.cleaned_data[self.form.DATE_TO]
        users = self.get_users(date_from, date_to)
        feedback_types = models.Feedback.objects.all()
        feedback_counts = self.get_feedback_counts(
            users, feedback_types, date_from, date_to
        )
        for user in users:
            user["feedback_counts"] = feedback_counts[user["id"]]
            user["full_name"] = " ".join((user["first_name"], user["second_name"]))
        context["users"] = users
        context["feedback_types"] = feedback_types
        context["form"] = self.form
        return context

    def get_users(self, date_from, date_to):
        """Return a list of users annotated with pack counts."""
        return (
            Staff.unhidden.order_by("first_name", "second_name")
            .annotate(
                pack_count=Count(
                    "packed_orders",
                    filter=Q(
                        packed_orders__dispatched_at__gte=date_from,
                        packed_orders__dispatched_at__lte=date_to
                        + datetime.timedelta(days=1),
                    ),
                )
            )
            .values()
        )

    def get_feedback_counts(self, users, feedback_types, date_from, date_to):
        """Return a dict of user feedback counts."""
        qs = (
            models.UserFeedback.objects.filter(user__hidden=False)
            .annotate(cc_user_id=F("user__pk"), feedback_id=F("feedback_type__pk"))
            .values("cc_user_id", "feedback_id")
            .annotate(
                count=Count(
                    "pk", filter=Q(timestamp__gte=date_from, timestamp__lte=date_to)
                )
            )
            .order_by("cc_user_id", "feedback_id")
        )
        feedback_counts = {}
        for user in users:
            feedback_counts[user["id"]] = {}
            for feedback_type in feedback_types:
                feedback_counts[user["id"]][feedback_type.id] = {
                    "pk": feedback_type.pk,
                    "name": feedback_type.name,
                    "image_url": feedback_type.image.url,
                    "count": 0,
                }
                for result in qs:
                    user_id = result["cc_user_id"]
                    feedback_id = result["feedback_id"]
                    if user_id == user["id"] and feedback_id == feedback_type.id:
                        feedback_counts[user["id"]][feedback_type.id]["count"] = result[
                            "count"
                        ]
                        continue
        return feedback_counts


class CreateUserFeedback(FeedbackUserMixin, CreateView):
    """View for create user feedback page."""

    model = models.UserFeedback
    fields = ["user", "timestamp", "feedback_type", "order_id", "note"]
    template_name = "feedback/user_feedback_form.html"
    success_url = reverse_lazy("feedback:user_feedback")

    def get_initial(self):
        """Return initial values for form."""
        initial = super().get_initial()
        user_id = self.kwargs["user_id"]
        initial["user"] = get_object_or_404(Staff, id=user_id)
        return initial

    def get_form(self, *args, **kwargs):
        """Add HTML class to the timestamp field."""
        form = super().get_form(*args, **kwargs)
        form.fields["timestamp"].widget.attrs["class"] = "datepicker"
        return form


class UpdateUserFeedback(FeedbackUserMixin, UpdateView):
    """View for update user feedback page."""

    model = models.UserFeedback
    fields = ["user", "timestamp", "feedback_type", "order_id", "note"]
    template_name = "feedback/user_feedback_form.html"
    success_url = reverse_lazy("feedback:user_feedback")

    def get_object(self):
        """Return UserFeedback object to update."""
        return get_object_or_404(self.model, id=self.kwargs.get("feedback_id"))

    def get_form(self, *args, **kwargs):
        """Add HTML class to the timestamp field."""
        form = super().get_form(*args, **kwargs)
        form.fields["timestamp"].widget.attrs["class"] = "datepicker"
        return form


class DeleteUserFeedback(FeedbackUserMixin, DeleteView):
    """View for deleting user feedback."""

    model = models.UserFeedback
    success_url = reverse_lazy("feedback:user_feedback")

    def get(self, *args, **kwargs):
        """Prevent GET requests."""
        return HttpResponseNotAllowed(["POST"])


class SafePaginator(Paginator):
    """Subclass paginator to handle invalid page numbers gracefully."""

    def validate_number(self, number):
        """
        Return valid page number.

        If requested page number is greater than the number of pages available
        return the last page number that is valid.
        """
        try:
            return super(SafePaginator, self).validate_number(number)
        except EmptyPage:
            if number > 1:
                return self.num_pages
            else:
                raise


class FeedbackList(FeedbackUserMixin, ListView):
    """View for displaying user feedback."""

    paginator_class = SafePaginator
    template_name = "feedback/feedback_list.html"
    model = models.UserFeedback
    paginate_by = 50
    context_object_name = "feedback_list"
    user = None
    feedback_type = None

    def get(self, *args, **kwargs):
        """Process GET request."""
        user_id = self.request.GET.get("user_id") or None
        if user_id is not None:
            self.user = get_object_or_404(Staff, pk=user_id)
        feedback_id = self.request.GET.get("feedback_id") or None
        if feedback_id is not None:
            self.feedback_type = get_object_or_404(models.Feedback, pk=feedback_id)
        form = forms.FeedbackSearchForm(self.request.GET)
        if form.is_valid():
            self.user = form.cleaned_data.get("user")
            self.feedback_type = form.cleaned_data.get("feedback")
            self.paginate_by = form.cleaned_data.get("paginate_by") or self.paginate_by
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Filter feedback according to form data."""
        queryset = self.model.objects.all()
        if self.user is not None:
            queryset = queryset.filter(user=self.user)
        if self.feedback_type is not None:
            queryset = queryset.filter(feedback_type=self.feedback_type)
        queryset = queryset.order_by("-timestamp")
        return queryset

    def get_initial(self):
        """Return initial data for form."""
        initial = {}
        if self.user is not None:
            initial["user"] = self.user.pk
        if self.feedback_type is not None:
            initial["feedback"] = self.feedback_type.pk
        initial["paginate_by"] = self.paginate_by
        return initial

    def get_context_data(self):
        """Return context data for template."""
        context = super().get_context_data()
        context["feedback_user"] = self.user
        context["feedback_type"] = self.feedback_type
        context["form"] = forms.FeedbackSearchForm(self.get_initial())
        return context


class FeedbackDetails(FeedbackUserMixin, TemplateView):
    """View for feedback details page."""

    template_name = "feedback/feedback_details.html"

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        feedback_id = self.kwargs.get("feedback_id")
        context["feedback"] = get_object_or_404(models.UserFeedback, id=feedback_id)
        return context


class Monitor(TemplateView):
    """View for feedback display."""

    template_name = "feedback/monitor.html"

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
        users = list(Staff.unhidden.all())
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
