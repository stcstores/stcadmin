import json

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from stcadmin import settings

import labeler
from labelmaker.models import SizeChart, SizeChartSize


@login_required(login_url=settings.LOGIN_URL)
def index(request):
    size_charts = SizeChart.objects.all()
    return render(
        request, 'labelmaker/index.html', {'size_charts': size_charts})


@login_required(login_url=settings.LOGIN_URL)
def create_size_chart(request):
    data = json.loads(request.POST['data'])
    size_chart = SizeChart(name=data['size_chart_name'])
    size_chart.save()
    for size_data in data['size_conversions']:
        size = SizeChartSize(
            size_chart=size_chart, sort=size_data['sort'],
            name=size_data['name'], uk_size=size_data['uk_size'],
            eu_size=size_data['eu_size'], us_size=size_data['us_size'],
            au_size=size_data['au_size'])
        size.save()
    return redirect(size_chart)


@login_required(login_url=settings.LOGIN_URL)
def edit_size_chart(request, size_chart_id):
    data = json.loads(request.POST['data'])
    size_chart = SizeChart.objects.get(pk=size_chart_id)
    size_chart_name = data['size_chart_name']
    if size_chart.name != size_chart_name:
        size_chart.name = size_chart_name
        size_chart.save()
    for size_data in data['size_conversions']:
        if size_data['action'] == 'create':
            size = SizeChartSize(
                size_chart=size_chart, sort=size_data['sort'],
                name=size_data['name'], uk_size=size_data['uk_size'],
                eu_size=size_data['eu_size'], us_size=size_data['us_size'],
                au_size=size_data['au_size'])
            size.save()
        else:
            size = SizeChartSize.objects.get(pk=size_data['id'])
            if size_data['action'] == 'edit':
                size.sort = size_data['sort']
                size.name = size_data['name']
                size.uk_size = size_data['uk_size']
                size.eu_size = size_data['eu_size']
                size.us_size = size_data['us_size']
                size.au_size = size_data['au_size']
                size.save()
            elif size_data['action'] == 'delete':
                size.delete()
    return redirect(size_chart)


@login_required(login_url=settings.LOGIN_URL)
def create_size_chart_form(request):
    return render(request, 'labelmaker/size_chart_form.html')


@login_required(login_url=settings.LOGIN_URL)
def edit_size_chart_form(request, size_chart_id):
    size_chart = SizeChart.objects.get(pk=size_chart_id)
    sizes = size_chart.sizechartsize_set.all()
    return render(request, 'labelmaker/size_chart_form.html', {
        'size_chart': size_chart, 'sizes': sizes})


@login_required(login_url=settings.LOGIN_URL)
def size_charts(request):
    size_charts = SizeChart.objects.all()
    return render(request, 'labelmaker/size_charts.html', {
        'size_charts': size_charts})


@login_required(login_url=settings.LOGIN_URL)
def label_form_size_chart(request, size_chart_id):
    size_chart = SizeChart.objects.get(pk=size_chart_id)
    sizes = size_chart.sizechartsize_set.all()
    return render(request, 'labelmaker/label_form_size_chart.html', {
        'size_chart': size_chart, 'sizes': sizes})


@login_required(login_url=settings.LOGIN_URL)
def label_form_no_size_chart(request):
    return render(request, 'labelmaker/label_form_no_size_chart.html')


@login_required(login_url=settings.LOGIN_URL)
def generate_pdf_no_size_chart(request):
    product_code = request.POST['product_code']
    data = []
    for item in json.loads(request.POST['data']):
        for number in range(int(item['quantity'])):
            data.append([item['size'], item['colour'], product_code])
    return generate_pdf(data)


@login_required(login_url=settings.LOGIN_URL)
def generate_pdf_for_size_chart(request, size_chart_id):
    data = json.loads(request.POST['data'])
    product_code = request.POST['product_code']
    label_data = get_label_data_for_size_chart(
        product_code, data, size_chart_id)
    return generate_pdf(label_data)


def get_label_data_for_size_chart(product_code, json_data, size_chart_id):
    label_data = []
    for variation in json_data:
        size = SizeChartSize.objects.get(pk=variation['size'])
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


@login_required(login_url=settings.LOGIN_URL)
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
    size_chart = SizeChart.objects.get(pk=size_chart_id)
    size_chart.delete()
    return redirect(reverse('labelmaker:size_charts'))
