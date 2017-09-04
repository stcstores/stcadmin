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

    def get(self, request):
        orders = models.CloudCommerceOrder.objects.all().annotate(
            date=TruncDate('date_created')).values('date').annotate(
                count=Count('pk')).order_by('date')
        return self.make_chart(orders, 'barh')

    def get_days(self, orders):
        class Day:
            def __init__(self, name, index, colour):
                self.name = name
                self.colour = colour
                self.index = index
                self.x = []
                self.y = []

            def get_orders(self, orders):
                orders = (
                    order for order in orders if
                    order['date'].weekday() == self.index)
                for order in orders:
                    self.x.append(order['date'])
                    self.y.append(order['count'])

            def make_plot(self, plt):
                plt(self.x, self.y, label=self.name, color=self.colour)

        days = (
            Day('Monday', 0, 'r'),
            Day('Tuesday', 1, 'b'),
            Day('Wednesday', 2, 'b'),
            Day('Thursday', 3, 'b'),
            Day('Friday', 4, 'b'),
            Day('Saturday', 5, 'g'),
            Day('Sunday', 6, 'g'))
        for day in days:
            day.get_orders(orders)
        return days

    def make_chart(self, orders, chart_type='bar'):
        days = self.get_days(orders)
        for day in days:
            day.make_plot(getattr(plt, chart_type))
        plt.grid(True)
        plt.style.use('ggplot')
        plt.title('Orders for Date')
        plt.xlabel('Date')
        plt.ylabel('Order Count')
        html = mpld3.fig_to_html(plt.gcf())
        return HttpResponse(html)


class Charts(PrintAuditUserMixin, TemplateView):
    template_name = 'print_audit/charts.html'
