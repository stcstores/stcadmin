"""Views for home app."""

import subprocess
import sys

from django import get_version as get_django_version
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.base import TemplateView


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
        packages = self.get_command_response("pipenv run pip freeze").split("\n")
        return [self.parse_package(package) for package in packages if package]

    def parse_package(self, package_string):
        """Return a package name from pip freeze as a tuple of name and version."""
        if "git+" in package_string:
            name, ref = package_string.split("@")
            version = ref.split("#")[0]
        else:
            name, version = package_string.split("==")
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
