"""Views for the labelmaker app."""

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
    """View mixin to ensure user in in the labelmaker group."""

    groups = ["labelmaker"]


class Index(LabelmakerUserMixin, TemplateView):
    """View for the labelmaker landing page."""

    template_name = "labelmaker/index.html"


class ProductLabels(LabelmakerUserMixin, TemplateView):
    """View for creating product labels."""

    template_name = "labelmaker/product_labels.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context_data = super().get_context_data()
        context_data["size_charts"] = SizeChart.objects.all()
        return context_data


class SizeChartForm(FormView):
    """View for Size Chart form."""

    template_name = "labelmaker/size_chart.html"
    form_class = forms.SizeFormset

    def form_valid(self, form):
        """Update model object."""
        size_chart_name = form.data.get("size_chart_name")
        if str(form.instance.name) != size_chart_name:
            form.instance.name = size_chart_name
            form.instance.save()
        form.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context_data = super().get_context_data()
        context_data["formset"] = context_data.pop("form")
        return context_data

    def get_form_kwargs(self, *args, **kwargs):
        """Return kwargs for form."""
        kwargs = super().get_form_kwargs()
        self.size_chart_id = self.kwargs.get("pk")
        kwargs["instance"] = get_object_or_404(SizeChart, pk=self.size_chart_id)
        return kwargs

    def get_success_url(self):
        """Return URL to redirect to after successful submission."""
        return reverse_lazy("labelmaker:size_charts")


class CreateSizeChart(LabelmakerUserMixin, View):
    """View for create size chart page."""

    def dispatch(self, *args, **kwargs):
        """Create new size chart and redirct to it's edit page."""
        size_chart = SizeChart.objects.create(name="PLACEHOLDER NAME")
        SizeChartSize.objects.create(size_chart=size_chart)
        return redirect(size_chart.get_absolute_url())


class SizeCharts(LabelmakerUserMixin, TemplateView):
    """View for size chart edit page."""

    template_name = "labelmaker/size_charts.html"

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["size_charts"] = SizeChart.objects.all()
        return context_data


class ProductLabelFormSizeChart(LabelmakerUserMixin, TemplateView):
    """View for label form when using a size chart."""

    template_name = "labelmaker/product_label_form.html"

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        size_chart_id = self.kwargs.get("size_chart_id")
        context_data["size_chart"] = get_object_or_404(SizeChart, pk=size_chart_id)
        context_data["sizes"] = context_data["size_chart"].sizechartsize_set.all()
        return context_data


class ProductLabelFormNoSizeChart(LabelmakerUserMixin, TemplateView):
    """View for label form when not using a size chart."""

    template_name = "labelmaker/product_label_form.html"


class BasePDFLabelView(LabelmakerUserMixin, View):
    """Base class for views for printable label PDFs."""

    def dispatch(self, *args, **kwargs):
        """Create HTTP response."""
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'filename="labels.pdf"'
        sheet = self.get_label_sheet(*args, **kwargs)
        data = self.get_label_data(*args, **kwargs)
        canvas = sheet.generate_PDF_from_data(data)
        canvas._filename = response
        canvas.save()
        return response

    def get_label_sheet(self, *args, **kwargs):
        """Return a formatted label sheet."""
        return self.label_sheet(label_format=self.label_format)


class BaseProductPDFLabelView(BasePDFLabelView):
    """Base view for product PDF labels."""

    label_format = labeler.DefaultLabelFormat
    label_sheet = labeler.STW046025PO


class ProductLabelsPDFNoSizeChart(BaseProductPDFLabelView):
    """View for product labels created without a size chart."""

    def get_label_data(self, *args, **kwargs):
        """Return list containing lists of lines of text for each label."""
        self.product_code = self.request.POST["product_code"]
        data = []
        for item in json.loads(self.request.POST["data"]):
            for number in range(int(item["quantity"])):
                data.append([item["size"], item["colour"], self.product_code])
        return data


class ProductLabelsPDFFromSizeChart(BaseProductPDFLabelView):
    """View for product labels created with a size chart."""

    @staticmethod
    def split_list(li, n):
        """Split text lines to fit on label."""
        num = float(len(li)) / n
        split_list = [
            li[i : i + int(num)] for i in range(0, (n - 1) * int(num), int(num))
        ]
        split_list.append(li[(n - 1) * int(num) :])
        return split_list

    def get_label_data(self, *args, **kwargs):
        """Return list containing lists of lines of text for each label."""
        self.product_code = self.request.POST["product_code"]
        size_chart_id = self.kwargs.get("size_chart_id") or None
        data = json.loads(self.request.POST["data"])

        label_data = self.get_label_data_for_size_chart(
            self.product_code, data, size_chart_id
        )
        return label_data

    def get_label_data_for_size_chart(self, product_code, json_data, size_chart_id):
        """Return text lines for labels generated from a size chart."""
        label_data = []
        for variation in json_data:
            size = get_object_or_404(SizeChartSize, pk=variation["size"])
            colour = variation["colour"]

            foriegn_size_list = [
                "{}: {}".format(size[0], size[1])
                for size in size.get_sizes()
                if len(size[1]) > 0
            ]

            foriegn_size_data = [
                " ".join(li) for li in self.split_list(foriegn_size_list, 3)
            ]

            for i in range(int(variation["quantity"])):
                if size.name is not None and len(size.name) > 0:
                    size_name = size.name
                else:
                    size_name = "UK: " + size.uk_size
                label_data.append([size_name, colour, product_code])
                label_data.append(foriegn_size_data)
        return label_data


class TestProductPDFLabel(BaseProductPDFLabelView):
    """View to create a PDF of labels generated from test data."""

    def get_label_data(self, *args, **kwargs):
        """Create PDF labels using test data."""
        data = [
            ["UK 12", "Pink Cat Slipper", "FW987"],
            ['38" Regular Tall', "Grey Shoulders, Blue Body", "45632"],
            ["Medium", "Grey", "64535"],
            ["UK 12", "Pink Cat Slipper", "FW987"],
            ['38" Regular Tall', "Grey Shoulders, Blue Body", "45632"],
            ["Medium", "Grey", "64535"],
            ['38" Regular Tall', "Grey Shoulders, Blue Body", "45632"],
            ["Medium", "Grey", "64535"],
        ]
        return data


class DeleteSizeChart(LabelmakerUserMixin, DeleteView):
    """View to delete SizeChart objects."""

    model = SizeChart
    success_url = reverse_lazy("labelmaker:size_charts")

    def get_object(self, *args, **kwargs):
        """Return object to delete."""
        return get_object_or_404(SizeChart, pk=self.kwargs.get("size_chart_id"))
