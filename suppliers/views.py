import csv
import datetime
import json
import operator
from functools import reduce

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from home.views import UserInGroupMixin
from stcadmin import settings
from suppliers.models import StockItem, Supplier


def is_suppliers_user(user):
    return user.groups.filter(name__in=['suppliers'])


class SuppliersUserMixin(UserInGroupMixin):
    groups = ['suppliers']


class Index(SuppliersUserMixin, TemplateView):
    template_name = 'suppliers/supplier_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['suppliers'] = Supplier.objects.all()
        return context


class UpdateSupplier(SuppliersUserMixin, UpdateView):
    model = Supplier
    fields = ('name', 'email', 'phone')
    template_name = 'suppliers/supplier_form.html'

    def get_object(self):
        return get_object_or_404(self.model, id=self.kwargs.get('supplier_id'))


class CreateSupplier(SuppliersUserMixin, CreateView):
    model = Supplier
    fields = ('name', 'email', 'phone')
    template_name = 'suppliers/supplier_form.html'


class CreateItem(SuppliersUserMixin, CreateView):
    model = StockItem
    fields = (
        'product_code', 'supplier_title', 'box_quantity', 'linnworks_title',
        'linnworks_sku', 'supplier')
    template_name = 'suppliers/add_item.html'

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        if self.kwargs.get('supplier_pk'):
            initial['supplier'] = self.kwargs['supplier_pk']
        return initial


class SupplierSearch(SuppliersUserMixin, TemplateView):
    template_name = 'suppliers/supplier_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.method == 'POST':
            context['suppliers'] = self.get_queryest(
                self.request.POST['search_string'])
        else:
            context['suppliers'] = Supplier.objects.all()
        return context

    def get_queryest(self, search_string):
        search_words = search_string.split(' ')
        return reduce(operator.and_, (
            Supplier.objects.filter(
                name__icontains=word) for word in search_words))


class SupplierView(SuppliersUserMixin, TemplateView):
    template_name = 'suppliers/supplier.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        pk = kwargs.get('pk')
        context['supplier'] = get_object_or_404(Supplier, pk=pk)
        context['items'] = context['supplier'].stockitem_set.all()
        return context


class DeleteItem(SuppliersUserMixin, DeleteView):
    model = StockItem
    success_url = reverse_lazy('suppliers:supplier_list')

    def get_object(self):
        return get_object_or_404(StockItem, pk=self.kwargs.get('item_id'))


class DeleteSupplier(SuppliersUserMixin, DeleteView):
    model = Supplier
    success_url = reverse_lazy('suppliers:supplier_search')

    def get_object(self):
        return get_object_or_404(Supplier, pk=self.kwargs.get('supplier_id'))


class GetItemAJAX(SuppliersUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        item_id = request.kwargs.get('item_id')
        item = get_object_or_404(StockItem, pk=item_id)
        return HttpResponse(json.dumps({
            'product_code': item.product_code,
            'supplier_title': item.supplier_title,
            'box_quantity': item.box_quantity,
            'notes': item.notes,
        }))


class UpdateItemAJAX(SuppliersUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        item_id = request.kwargs.get('item_id')
        item = get_object_or_404(StockItem, pk=item_id)
        item.supplier_title = request.POST['supplier_title']
        item.product_code = request.POST['product_code']
        item.box_quantity = request.POST['box_quantity']
        item.notes = request.POST['notes']
        item.save()
        return HttpResponse('1')


class DeleteItemAJAX(SuppliersUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        item_id = request.kwargs.get('item_id')
        item = get_object_or_404(StockItem, pk=item_id)
        item.delete()
        return HttpResponse('1')


class ApiExport(SuppliersUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        if not request.user.groups.filter(name__in=['suppliers']):
            raise PermissionDenied
        item_id_quantity = json.loads(request.POST['item_id-quantity'])
        supplier = get_object_or_404(Supplier, pk=request.POST['supplier_id'])
        response = self.get_response(item_id_quantity, supplier)
        return response

    def get_filename(self, supplier_name):
        date_string = datetime.date.today().strftime("%d-%m-%Y")
        return '{} {} Order Items.csv'.format(date_string, supplier_name)

    def get_response(self, item_id_quantity, supplier):
        response = HttpResponse(content_type='text/csv')
        lines = [['Product Code', 'Item Title', 'Box Quantity', 'Quantity']]
        for item_id, quantity in item_id_quantity.items():
            item = get_object_or_404(StockItem, pk=item_id)
            lines.append([
                item.product_code, item.supplier_title, item.box_quantity,
                quantity])
        writer = csv.writer(response)
        writer.writerow([supplier.name])
        writer.writerow([])
        writer.writerow(['Phone', supplier.phone, '', 'Email', supplier.email])
        for line in lines:
            writer.writerow(line)
        response[
            'Content-Disposition'] = 'attachment; filename="{}"'.format(
                self.get_filename(supplier.name))
        return response
