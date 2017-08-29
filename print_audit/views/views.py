from django.views.generic.base import TemplateView
from home.views import UserInGroupMixin


class PrintAuditUserMixin(UserInGroupMixin):
    groups = ['print_audit']


class Index(PrintAuditUserMixin, TemplateView):
    template_name = 'print_audit/index.html'
