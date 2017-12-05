import json

import labeler
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView
from home.views import UserInGroupMixin
from labelmaker import forms
from labelmaker.models import SizeChart, SizeChartSize


class LabelmakerUserMixin(UserInGroupMixin):
    groups = ['labelmaker']


class Index(LabelmakerUserMixin, TemplateView):
    template_name = 'labelmaker/index.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data()
        context_data['size_charts'] = SizeChart.objects.all()
        return context_data


class SizeChartForm(FormView):

    template_name = 'labelmaker/size_chart.html'
    form_class = forms.SizeFormset

    def form_valid(self, form):
        size_chart_name = form.data.get('size_chart_name')
        if str(form.instance.name) != size_chart_name:
            form.instance.name = size_chart_name
            form.instance.save()
        form.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data()
        context_data['formset'] = context_data.pop('form')
        return context_data

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        self.size_chart_id = self.kwargs.get('pk')
        kwargs['instance'] = get_object_or_404(
            SizeChart, pk=self.size_chart_id)
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'labelmaker:size_chart_form',
            kwargs={'size_chart_id': self.size_chart_id})


class CreateSizeChart(LabelmakerUserMixin, View):

    def dispatch(self, *args, **kwargs):
        size_chart = SizeChart.objects.create(name='PLACEHOLDER NAME')
        SizeChartSize.objects.create(size_chart=size_chart)
        return redirect(size_chart.get_absolute_url())


class SizeCharts(LabelmakerUserMixin, TemplateView):
    template_name = 'labelmaker/size_charts.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['size_charts'] = SizeChart.objects.all()
        return context_data


class LabelFormSizeChart(LabelmakerUserMixin, TemplateView):
    template_name = 'labelmaker/label_form.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        size_chart_id = self.kwargs.get('size_chart_id')
        context_data['size_chart'] = get_object_or_404(
            SizeChart, pk=size_chart_id)
        context_data['sizes'] = context_data[
            'size_chart'].sizechartsize_set.all()
        return context_data


class LabelFormNoSizeChart(LabelmakerUserMixin, TemplateView):
    template_name = 'labelmaker/label_form.html'


class PDFLabelView(LabelmakerUserMixin, View):

    @staticmethod
    def generate_pdf_response(data):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="labels.pdf"'
        label_format = labeler.DefaultLabelFormat
        sheet = labeler.STW046025PO(label_format=label_format)
        canvas = sheet.generate_PDF_from_data(data)
        canvas._filename = response
        canvas.save()
        return response

    @staticmethod
    def split_list(li, n):
        num = float(len(li))/n
        split_list = [
            li[i:i + int(num)] for i in range(0, (n-1)*int(num), int(num))]
        split_list.append(li[(n-1)*int(num):])
        return split_list

    def get_label_data_for_size_chart(
                self, product_code, json_data, size_chart_id):
        label_data = []
        for variation in json_data:
            size = get_object_or_404(SizeChartSize, pk=variation['size'])
            colour = variation['colour']

            foriegn_size_list = [
                '{}: {}'.format(size[0], size[1]) for size in
                size.get_sizes() if len(size[1]) > 0]

            foriegn_size_data = [' '.join(li) for li in self.split_list(
                foriegn_size_list, 3)]

            for i in range(int(variation['quantity'])):
                if size.name is not None and len(size.name) > 0:
                    size_name = size.name
                else:
                    size_name = 'UK: ' + size.uk_size
                label_data.append([size_name, colour, product_code])
                label_data.append(foriegn_size_data)
        return label_data


class TestPDFLabel(PDFLabelView):

    def dispatch(self, *args, **kwargs):
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
        return self.generate_pdf_response(data)


class LabelPDF(PDFLabelView):

    def dispatch(self, *args, **kwargs):
        size_chart_id = self.kwargs.get('size_chart_id') or None
        if size_chart_id is None:
            return self.no_size_chart()
        return self.with_size_chart(size_chart_id)

    def no_size_chart(self):
        product_code = self.request.POST['product_code']
        data = []
        for item in json.loads(self.request.POST['data']):
            for number in range(int(item['quantity'])):
                data.append([item['size'], item['colour'], product_code])
        return self.generate_pdf_response(data)

    def with_size_chart(self, size_chart_id):
        data = json.loads(self.request.POST['data'])
        product_code = self.request.POST['product_code']
        label_data = self.get_label_data_for_size_chart(
            product_code, data, size_chart_id)
        return self.generate_pdf_response(label_data)


class DeleteSizeChart(LabelmakerUserMixin, DeleteView):
    model = SizeChart
    success_url = reverse_lazy('labelmaker:size_charts')

    def get_object(self, *args, **kwargs):
        return get_object_or_404(
            SizeChart, pk=self.kwargs.get('size_chart_id'))
