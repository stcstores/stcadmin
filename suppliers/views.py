from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
import operator
from functools import reduce
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from suppliers.models import Supplier, StockItem
from stcadmin import settings

import json
import csv
import datetime


@login_required(login_url=settings.LOGIN_URL)
def index(request):
    return supplier_list(request)


@login_required(login_url=settings.LOGIN_URL)
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(
        request, 'suppliers/supplier_list.html', {'suppliers': suppliers})


@login_required(login_url=settings.LOGIN_URL)
def supplier_search(request):
    if request.method == 'POST':
        search_string = request.POST['search_string']
        print(len(search_string))
        if len(search_string) > 0:
            search_words = search_string.split(' ')
            query = reduce(operator.and_, (
                Supplier.objects.filter(
                    name__icontains=word) for word in search_words))
            return render(
                request, 'suppliers/supplier_list.html', {'suppliers': query})
    query = Supplier.objects.all()
    return render(
        request, 'suppliers/supplier_list.html', {'suppliers': query})


@login_required(login_url=settings.LOGIN_URL)
def supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    items = supplier.stockitem_set.all()
    return render(request, 'suppliers/supplier.html', {
        'supplier': supplier, 'items': items})


@login_required(login_url=settings.LOGIN_URL)
def add_item(request):
    supplier_id = Supplier.objects.all()[0].id
    return add_item_to_supplier(request, supplier_id)


@login_required(login_url=settings.LOGIN_URL)
def add_item_to_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    suppliers = Supplier.objects.all()
    product_codes = StockItem.objects.order_by().values_list(
        'product_code', flat=True)
    return render(request, 'suppliers/add_item.html', {
        'supplier': supplier,
        'suppliers': suppliers,
        'product_codes': product_codes})


@login_required(login_url=settings.LOGIN_URL)
def create_item(request):
    try:
        supplier_id = request.POST['supplier']
        item_title = request.POST['item_title']
        product_code = request.POST['product_code']
        linnworks_title = request.POST['linnworks_title']
        linnworks_sku = request.POST['linnworks_sku']
        notes = request.POST['notes']
        new_item = StockItem(
            supplier_id=supplier_id, supplier_title=item_title,
            product_code=product_code, linnworks_title=linnworks_title,
            linnworks_sku=linnworks_sku, notes=notes)
        new_item.save()
        return redirect('suppliers:add_item', supplier_id)
    except Exception as e:
        return HttpResponse(
            '<h3>Item Creaton Error</h3><p>{}</p>'.format(str(e)))


@login_required(login_url=settings.LOGIN_URL)
def add_supplier(request):
    return render(request, 'suppliers/add_supplier.html')


@login_required(login_url=settings.LOGIN_URL)
def create_supplier(request):
    try:
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        supplier = Supplier(name=name, email=email, phone=phone)
        supplier.save()
        return redirect('suppliers:add_supplier')
    except Exception as e:
        return HttpResponse(
            '<h3>Supplier Creation Error</h3><p>{}</p>'.format(str(e)))


@login_required(login_url=settings.LOGIN_URL)
def delete_item(request, item_id):
    item = StockItem.objects.get(pk=item_id)
    item.delete()
    return redirect('suppliers:supplier_list')


@login_required(login_url=settings.LOGIN_URL)
def delete_supplier(request, supplier_id):
    supplier = Supplier.objects.get(pk=supplier_id)
    supplier.delete()
    return redirect('suppliers:supplier_search')


@login_required(login_url=settings.LOGIN_URL)
def api_get_item(request, item_id):
    item = StockItem.objects.get(pk=item_id)
    return HttpResponse(json.dumps({
        'product_code': item.product_code,
        'supplier_title': item.supplier_title,
        'notes': item.notes,
        'linnworks_title': item.linnworks_title
    }))


@login_required(login_url=settings.LOGIN_URL)
def api_update_item(request, item_id):
    item = StockItem.objects.get(pk=item_id)
    item.supplier_title = request.POST['supplier_title']
    item.product_code = request.POST['product_code']
    item.linnworks_title = request.POST['linnworks_title']
    item.notes = request.POST['notes']
    item.save()
    return HttpResponse('1')


@login_required(login_url=settings.LOGIN_URL)
def api_delete_item(request, item_id):
    item = get_object_or_404(StockItem, pk=item_id)
    item.delete()
    return HttpResponse('1')


class ApiExport():

    def get_filename(self, supplier_name):
        date_string = datetime.date.today().strftime("%d-%m-%Y")
        return '{} {} Order Items.csv'.format(date_string, supplier_name)

    def get_response(self, item_id_quantity, supplier):
        response = HttpResponse(content_type='text/csv')
        lines = [['Product Code', 'Item Title', 'Quantity']]
        for item_id, quantity in item_id_quantity.items():
            item = StockItem.objects.get(pk=item_id)
            lines.append([item.product_code, item.supplier_title, quantity])
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

    @login_required(login_url=settings.LOGIN_URL)
    def as_view(self, request):
        item_id_quantity = json.loads(request.POST['item_id-quantity'])
        supplier = Supplier.objects.get(pk=request.POST['supplier_id'])
        response = self.get_response(item_id_quantity, supplier)
        return response
