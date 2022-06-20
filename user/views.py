"""Views for the User app."""

from django.contrib.auth import logout
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import reverse
from django.views.generic.base import RedirectView, TemplateView

from feedback import models
from home.models import Staff
from home.views import UserLoginMixin


class User(UserLoginMixin, TemplateView):
    """View for the User page."""

    template_name = "user/user.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        context["feedback_count"] = self.get_feedback_count()
        return context

    def get_feedback_count(self):
        """Return dict of feedback counts by feedback type for current user."""
        try:
            user = Staff.objects.get(stcadmin_user=self.request.user)
        except Staff.DoesNotExist:
            return {}
        else:
            feedback_types = models.Feedback.objects.all()
            feedback_count = {
                feedback_type: models.UserFeedback.objects.filter(
                    user=user.pk, feedback_type=feedback_type
                ).count()
                for feedback_type in feedback_types
            }
            return feedback_count


class ChangePassword(UserLoginMixin, PasswordChangeView):
    """Allow user to change their password."""

    template_name = "user/change_password.html"


class ChangePasswordDone(UserLoginMixin, RedirectView):
    """Landing page after succesful password update."""

    def get_redirect_url(self, *args, **kwargs):
        """Logout user."""
        logout(self.request)
        return reverse("home:login_user")
