import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View

from stcadmin import settings

import labeler
from labelmaker.models import SizeChart, SizeChartSize


def is_labelmaker_user(user):
    return user.groups.filter(name__in=['labelmaker'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_labelmaker_user)
def index(request):
    size_charts = SizeChart.objects.all()
    return render(
        request, 'labelmaker/index.html', {'size_charts': size_charts})


class EditSizeChart(View):
    def post(self, request, size_chart_id=None):
        if not request.user.groups.filter(name__in=['labelmaker']):
            raise PermissionDenied
        self.data = json.loads(request.POST['data'])
        if size_chart_id is None:
            self.create_size_chart()
        else:
            self.size_chart = get_object_or_404(SizeChart, pk=size_chart_id)
            self.update_size_chart_name()
            for size_data in self.data['size_conversions']:
                self.update_size_conversion(size_data)
        return redirect(self.size_chart)

    def create_size_chart(self):
        self.size_chart = SizeChart(name=self.data['size_chart_name'])
        self.size_chart.save()
        for size_data in self.data['size_conversions']:
            size = SizeChartSize(
                size_chart=self.size_chart, sort=size_data['sort'],
                name=size_data['name'], uk_size=size_data['uk_size'],
                eu_size=size_data['eu_size'], us_size=size_data['us_size'],
                au_size=size_data['au_size'])
            size.save()

    def update_size_chart_name(self):
        size_chart_name = self.data['size_chart_name']
        if self.size_chart.name != size_chart_name:
            self.size_chart.name = size_chart_name
            self.size_chart.save()

    def update_size_conversion(self, size_data):
        if size_data['action'] == 'create':
            self.create_size_from_edit_size_chart(self.size_chart, size_data)
        else:
            size = get_object_or_404(SizeChartSize, pk=size_data['id'])
            if size_data['action'] == 'edit':
                self.edit_size_from_edit_size_chart(size, size_data)
            elif size_data['action'] == 'delete':
                size.delete()

    def create_size_from_edit_size_chart(self, size_chart, size_data):
        size = SizeChartSize(
            size_chart=size_chart, sort=size_data['sort'],
            name=size_data['name'], uk_size=size_data['uk_size'],
            eu_size=size_data['eu_size'], us_size=size_data['us_size'],
            au_size=size_data['au_size'])
        size.save()

    def edit_size_from_edit_size_chart(self, size, size_data):
        size.sort = size_data['sort']
        size.name = size_data['name']
        size.uk_size = size_data['uk_size']
        size.eu_size = size_data['eu_size']
        size.us_size = size_data['us_size']
        size.au_size = size_data['au_size']
        size.save()


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_labelmaker_user)
def create_size_chart_form(request):
    return render(request, 'labelmaker/size_chart_form.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_labelmaker_user)
def edit_size_chart_form(request, size_chart_id):
    size_chart = get_object_or_404(SizeChart, pk=size_chart_id)
    sizes = size_chart.sizechartsize_set.all()
    return render(request, 'labelmaker/size_chart_form.html', {
        'size_chart': size_chart, 'sizes': sizes})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_labelmaker_user)
def size_charts(request):
    size_charts = SizeChart.objects.all()
    return render(request, 'labelmaker/size_charts.html', {
        'size_charts': size_charts})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_labelmaker_user)
def label_form_size_chart(request, size_chart_id):
    size_chart = get_object_or_404(SizeChart, pk=size_chart_id)
    sizes = size_chart.sizechartsize_set.all()
    return render(request, 'labelmaker/label_form.html', {
        'size_chart': size_chart, 'sizes': sizes})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_labelmaker_user)
def label_form_no_size_chart(request):
    return render(request, 'labelmaker/label_form.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_labelmaker_user)
def generate_pdf_no_size_chart(request):
    product_code = request.POST['product_code']
    data = []
    for item in json.loads(request.POST['data']):
        for number in range(int(item['quantity'])):
            data.append([item['size'], item['colour'], product_code])
    return generate_pdf(data)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_labelmaker_user)
def generate_pdf_for_size_chart(request, size_chart_id):
    data = json.loads(request.POST['data'])
    product_code = request.POST['product_code']
    label_data = get_label_data_for_size_chart(
        product_code, data, size_chart_id)
    return generate_pdf(label_data)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_labelmaker_user)
def test_pdf(request):
    data = [
        ['UK 12', 'Pink Cat Slipper', 'FW987'],
        ['38" Regular Tall', 'Grey Shoulders, Blue Body', '45632'],
        ['Medium', 'Grey', '64535'],
        ['UK 12', 'Pink Cat Slipper', 'FW987'],
        ['38" Regular Tall', 'Grey Shoulders, Blue Body', '45632'],
        ['Medium', 'Grey', '64535'],
        ['38" Regular Tall', 'Grey Shoulders, Blue Body', '45632'],
        ['Medium', 'Grey', '64535']
    ]
    return generate_pdf(data)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="labels.pdf"'
    sheet = labeler.LabelSheet(labeler.A4, labeler.DefaultLabelSize)

    canvas = sheet.generate_PDF_from_data(data)
    canvas._filename = response
    canvas.save()
    return response


@login_required(login_url=settings.LOGIN_URL)
def delete_size_chart(request, size_chart_id):
    size_chart = get_object_or_404(SizeChart, pk=size_chart_id)
    size_chart.delete()
    return redirect(reverse('labelmaker:size_charts'))


def get_label_data_for_size_chart(product_code, json_data, size_chart_id):
    label_data = []
    for variation in json_data:
        size = get_object_or_404(SizeChartSize, pk=variation['size'])
        colour = variation['colour']

        foriegn_size_list = [
            '{}: {}'.format(size[0], size[1]) for size in
            size.get_sizes() if len(size[1]) > 0]

        foriegn_size_data = [' '.join(li) for li in split_list(
            foriegn_size_list, 3)]

        for i in range(int(variation['quantity'])):
            if size.name is not None and len(size.name) > 0:
                size_name = size.name
            else:
                size_name = 'UK: ' + size.uk_size
            label_data.append([size_name, colour, product_code])
            label_data.append(foriegn_size_data)
    return label_data


def generate_pdf(data):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="labels.pdf"'
    label_format = labeler.DefaultLabelFormat
    sheet = labeler.STW046025PO(label_format=label_format)
    canvas = sheet.generate_PDF_from_data(data)
    canvas._filename = response
    canvas.save()
    return response


def split_list(li, n):
    num = float(len(li))/n
    l = [li[i:i + int(num)] for i in range(0, (n-1)*int(num), int(num))]
    l.append(li[(n-1)*int(num):])
    return l
