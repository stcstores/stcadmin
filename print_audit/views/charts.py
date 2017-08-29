from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from print_audit import models

from .views import PrintAuditUserMixin

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa
import mpld3  # noqa


class GetChart(PrintAuditUserMixin, View):

    def get_chart(self, request):
        orders = models.CloudCommerceOrder.objects.all().annotate(
            date=TruncDate('date_created')).values('date').annotate(
                count=Count('pk')).order_by('date')
        return make_chart(orders, 'barh')


def make_chart(orders, chart_type='bar'):
    x = [order['date'] for order in orders]
    y = [order['count'] for order in orders]
    getattr(plt, chart_type)(x, y)
    plt.grid(True)
    plt.style.use('ggplot')
    plt.title('Orders for Date')
    plt.xlabel('Date')
    plt.ylabel('Order Count')
    html = mpld3.fig_to_html(plt.gcf())
    return HttpResponse(html)


class Charts(PrintAuditUserMixin, TemplateView):
    template_name = 'print_audit/charts.html'
