from django.views.generic.base import TemplateView
from home.views import UserInGroupMixin


class CloudCommerceUserMixin(UserInGroupMixin):
    groups = ['cloud_commerce']


class Index(CloudCommerceUserMixin, TemplateView):
    template_name = 'cloud_commerce/index.html'
