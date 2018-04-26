"""Views for home app."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.base import TemplateView

from stcadmin import settings


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

    template_name = 'home/index.html'
