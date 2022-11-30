"""Views for home app."""

import subprocess
import sys

import pkg_resources
from django import get_version as get_django_version
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import reverse
from django.views.generic.base import RedirectView, TemplateView

from feedback.models import Feedback, UserFeedback
from home import models


class UserLoginMixin(LoginRequiredMixin):
    """View mixin to enusure request comes from a logged in user."""

    login_url = settings.LOGIN_URL


class UserInGroupMixin(UserLoginMixin, UserPassesTestMixin):
    """View mixin to ensure user is logged in and in a given group."""

    def test_func(self):
        """Test user is in a group."""
        return self.request.user.groups.filter(name__in=self.groups)


class Index(LoginRequiredMixin, TemplateView):
    """View for homepage."""

    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["external_links"] = models.ExternalLink.objects.all()
        return context


class Version(TemplateView):
    """View for version information page."""

    template_name = "home/version.html"

    def get_command_response(self, command):
        """Retrun the stdout of a console command."""
        command_list = command.split(" ")
        result = subprocess.run(command_list, stdout=subprocess.PIPE)
        return result.stdout.decode("utf-8")

    def get_pip_packages(self):
        """Return a list of installed pip packages."""
        return [self.parse_package(package) for package in pkg_resources.working_set]

    def parse_package(self, package_string):
        """Return a package name from pip freeze as a tuple of name and version."""
        name, version = str(package_string).split(" ")
        return {"name": name, "version": version}

    def get_current_commit_hash(self):
        """Return the current checked out commit."""
        return self.get_command_response("git log --pretty=format:'%H' -n 1")[1:-1]

    def get_current_commit_message(self):
        """Return the current checked out commit."""
        return self.get_command_response("git log --pretty=format:'%B' -n 1")[1:-1]

    def get_context_data(self, *args, **kwargs):
        """Return the context for the rendered template."""
        context = super().get_context_data(*args, **kwargs)
        context["python_version"] = sys.version
        context["django_version"] = get_django_version()
        context["pip_list"] = self.get_pip_packages()
        context["commit_hash"] = self.get_current_commit_hash()
        context["commit_message"] = self.get_current_commit_message()
        return context


class DisplayMonitor(TemplateView):
    """View for display monitor."""

    template_name = "home/monitor.html"


class User(UserLoginMixin, TemplateView):
    """View for the User page."""

    template_name = "home/user.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        context["feedback_count"] = self.get_feedback_count()
        return context

    def get_feedback_count(self):
        """Return dict of feedback counts by feedback type for current user."""
        try:
            user = models.Staff.objects.get(stcadmin_user=self.request.user)
        except models.Staff.DoesNotExist:
            return {}
        else:
            feedback_types = Feedback.objects.all()
            feedback_count = {
                feedback_type: UserFeedback.objects.filter(
                    user=user.pk, feedback_type=feedback_type
                ).count()
                for feedback_type in feedback_types
            }
            return feedback_count


class ChangePassword(UserLoginMixin, PasswordChangeView):
    """Allow user to change their password."""

    template_name = "home/change_password.html"


class ChangePasswordDone(UserLoginMixin, RedirectView):
    """Landing page after succesful password update."""

    def get_redirect_url(self, *args, **kwargs):
        """Logout user."""
        logout(self.request)
        return reverse("home:login_user")
