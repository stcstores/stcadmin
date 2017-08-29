from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from stcadmin import settings


class UserLoginMixin(LoginRequiredMixin):
    login_url = settings.LOGIN_URL


class UserInGroupMixin(UserLoginMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.groups.filter(name__in=self.groups)


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'home/index.html'
