from django.views.generic.base import TemplateView
from home.views import UserInGroupMixin


class SpringUserMixin(UserInGroupMixin):
    groups = ['spring']


class Index(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/index.html'
