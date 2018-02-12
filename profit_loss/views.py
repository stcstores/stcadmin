import csv
import datetime
from io import StringIO

import pytz
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import is_naive
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView

from home.views import UserInGroupMixin
from profit_loss import models


def localise_datetime(date_input):
    if date_input is not None and is_naive(date_input):
        tz = pytz.timezone('Europe/London')
        date_input = date_input.replace(tzinfo=tz)
    return date_input


class ProfitLossUserMixin(UserInGroupMixin):
    groups = ['profit_loss']


class Orders(ProfitLossUserMixin, ListView):
    paginator_class = Paginator
    template_name = 'profit_loss/orders.html'
    model = models.Order
    paginate_by = 100
    context_object_name = 'orders'
    start_date = None
    end_date = None

    def get(self, *args, **kwargs):
        if self.request.GET.get('date_from'):
            year, month, day = self.request.GET['date_from'].split('-')
            self.start_date = localise_datetime(datetime.datetime(
                year=int(year), month=int(month), day=int(day)))
        if self.request.GET.get('date_to'):
            year, month, day = self.request.GET['date_to'].split('-')
            self.end_date = localise_datetime(datetime.datetime(
                year=int(year), month=int(month), day=int(day)))
        return super().get(*args, **kwargs)

    def get_queryset(self):
        orders = self.model.objects
        if self.start_date is not None:
            orders = orders.filter(date_recieved__gte=self.start_date)
        if self.end_date is not None:
            orders = orders.filter(date_recieved__lte=self.end_date)
        return orders.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


class Order(ProfitLossUserMixin, TemplateView):
    template_name = 'profit_loss/order.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        order_id = self.kwargs.get('order_id')
        context['order'] = get_object_or_404(models.Order, id=order_id)
        return context


class ExportOrders(View):
    start_date = None
    end_date = None

    def dispatch(self, *args, **kwargs):
        self.request = args[0]
        output = StringIO()
        self.orders = self.get_orders()
        header = self.header()
        data = self.get_data()
        writer = csv.writer(output, csv.QUOTE_NONNUMERIC)
        writer.writerow(header)
        for row in data:
            writer.writerow(row)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            self.get_filename())
        return response

    def get_orders(self):
        if self.request.POST.get('date_from'):
            year, month, day = self.request.POST['date_from'].split('-')
            self.start_date = localise_datetime(datetime.datetime(
                year=int(year), month=int(month), day=int(day)))
        if self.request.POST.get('date_to'):
            year, month, day = self.request.POST['date_to'].split('-')
            self.end_date = localise_datetime(datetime.datetime(
                year=int(year), month=int(month), day=int(day)))
        orders = models.Order.objects.filter()
        if self.start_date is not None:
            orders = orders.filter(date_recieved__gte=self.start_date)
        if self.end_date is not None:
            orders = orders.filter(date_recieved__lte=self.end_date)
        return orders.all()

    def format_price(self, price):
        if price is None:
            return '-'
        return '£{price:.2f}'.format(price=float(price / 100))

    def get_filename(self):
        date_format = '%Y-%m-%d'
        if self.start_date is not None and self.end_date is not None:
            return 'profit_loss_{}_to_{}.csv'.format(
                self.start_date.strftime(date_format),
                self.end_date.strftime(date_format))
        if self.start_date:
            return 'profit_loss_{}_on.csv'.format(
                self.start_date.strftime(date_format))
        if self.end_date:
            return 'profit_loss_to_{}.csv'.format(
                self.end_date.strftime(date_format))
        return 'profit_loss.csv'

    def header(self):
        return [
            'Order ID', 'Department', 'Country', 'Items', 'Price',
            'Weight (g)', 'Courier Rule', 'Postage Price', 'Purchase Price',
            'Channel Fee', 'VAT', 'Profit (with VAT)', 'Profit', 'Profit %']

    def get_data(self):
        return [[
            order.order_id, order.department, order.country, order.item_count,
            self.format_price(order.price), order.weight,
            order.shipping_service, self.format_price(order.postage_price),
            self.format_price(order.purchase_price),
            self.format_price(order.channel_fee()),
            self.format_price(order.vat()),
            self.format_price(order.profit_no_vat()),
            self.format_price(order.profit()),
            str(order.profit_percentage()) + '%'] for order in self.orders]
