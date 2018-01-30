from django.views.generic.base import TemplateView

from home.views import UserInGroupMixin
from print_audit import charts


class PrintAuditUserMixin(UserInGroupMixin):
    groups = ['print_audit']


class Index(PrintAuditUserMixin, TemplateView):
    template_name = 'print_audit/index.html'


class Charts(PrintAuditUserMixin, TemplateView):
    template_name = 'print_audit/charts.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['orders_by_week_chart'] = charts.OrdersByWeek()
        context['orders_by_day_chart'] = charts.OrdersByDay()
        return context
