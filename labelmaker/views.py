"""Views for the labelmaker app."""

import json

import labeler
from django import http
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView

from home.views import UserInGroupMixin
from labelmaker import forms, models


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
        context_data["size_charts"] = models.SizeChart.by_supplier()
        return context_data


class CreateSizeChart(LabelmakerUserMixin, CreateView):
    """Create a SizeChart object."""

    model = models.SizeChart
    fields = ["supplier", "name"]

    def get_success_url(self):
        """Redirect to the size form."""
        models.SizeChartSize.objects.create(size_chart=self.object)
        return self.object.get_edit_sizes_url()


class UpdateSizeChart(LabelmakerUserMixin, UpdateView):
    """Update a SizeChart object."""

    model = models.SizeChart
    fields = ["supplier", "name"]

    def get_success_url(self):
        """Redirect to edit the size chart's sizes."""
        return self.object.get_edit_sizes_url()


class DeleteSizeChart(LabelmakerUserMixin, DeleteView):
    """Delete a SizeChart object."""

    model = models.SizeChart
    success_url = reverse_lazy("labelmaker:product_labels")

    def get_object(self, *args, **kwargs):
        """Return object to delete."""
        return get_object_or_404(self.model, id=self.kwargs.get("id"))


class EditSizeChartSizes(LabelmakerUserMixin, FormView):
    """View for Size Chart form."""

    template_name = "labelmaker/size_chart_sizes.html"
    form_class = forms.SizeFormset

    def form_valid(self, form):
        """Update model object."""
        form.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context_data = super().get_context_data()
        context_data["formset"] = context_data.pop("form")
        context_data["size_chart"] = context_data["formset"].instance
        return context_data

    def get_form_kwargs(self, *args, **kwargs):
        """Return kwargs for form."""
        kwargs = super().get_form_kwargs()
        self.size_chart_id = self.kwargs.get("id")
        kwargs["instance"] = get_object_or_404(models.SizeChart, id=self.size_chart_id)
        return kwargs

    def get_success_url(self):
        """Return URL to redirect to after successful submission."""
        return reverse_lazy("labelmaker:product_labels")


class CreateProductLabelsWithTemplate(LabelmakerUserMixin, TemplateView):
    """View for label form when using a size chart."""

    template_name = "labelmaker/create_product_labels.html"

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context_data = super().get_context_data(*args, **kwargs)
        size_chart_id = self.kwargs.get("id")
        context_data["size_chart"] = get_object_or_404(
            models.SizeChart, id=size_chart_id
        )
        context_data["sizes"] = context_data["size_chart"].sizechartsize_set.all()
        return context_data


class CreateProductLabelsWithoutTemplate(LabelmakerUserMixin, TemplateView):
    """View for label form when not using a size chart."""

    template_name = "labelmaker/create_product_labels.html"


class BasePDFLabelView(LabelmakerUserMixin, View):
    """Base class for views for printable label PDFs."""

    def post(self, *args, **kwargs):
        """Create HTTP response."""
        return self.create_label_response(*args, **kwargs)

    def create_label_response(self, *args, **kwargs):
        """Return an HttpResponse object with the generated label PDF."""
        response = http.HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'filename="labels.pdf"'
        sheet = self.get_label_sheet(*args, **kwargs)
        data = self.get_label_data(*args, **kwargs)
        canvas = sheet.generate_PDF_from_data(data)
        canvas._filename = response
        self.edit_canvas(canvas)
        canvas.save()
        return response

    def get_label_sheet(self, *args, **kwargs):
        """Return a formatted label sheet."""
        return self.label_sheet(label_format=self.label_format)

    def edit_canvas(self, canvas):
        """Make changes to the canvas after label generation."""
        pass


class BaseProductPDFLabelView(BasePDFLabelView):
    """Base view for product PDF labels."""

    label_format = labeler.DefaultLabelFormat
    label_sheet = labeler.STW046025PO

    def read_json(self):
        """Return label data from POST data."""
        return json.loads(self.request.POST.get("data"))


class ProductLabelsPDFNoSizeChart(BaseProductPDFLabelView):
    """View for product labels created without a size chart."""

    def get_label_data(self, *args, **kwargs):
        """Return list containing lists of lines of text for each label."""
        self.product_code = self.request.POST["product_code"]
        data = []
        for item in self.read_json():
            for _ in range(int(item["quantity"])):
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
        product_code = self.request.POST.get("product_code")
        size_chart = get_object_or_404(models.SizeChart, id=self.kwargs.get("id"))
        label_input = self.read_json()
        label_data = self.get_label_data_for_size_chart(
            product_code, label_input, size_chart
        )
        return label_data

    def get_label_data_for_size_chart(self, product_code, label_input, size_chart):
        """Return text lines for labels generated from a size chart."""
        label_data = []
        for label in label_input:
            size = get_object_or_404(
                models.SizeChartSize, id=label["size"], size_chart=size_chart
            )
            colour = label["colour"]
            foriegn_size_data = self.foriegn_size_data(size)
            for _ in range(int(label["quantity"])):
                if size.name:
                    size_name = size.name
                else:
                    size_name = "UK: " + size.uk_size
                label_data.append([size_name, colour, product_code])
                label_data.append(foriegn_size_data)
        return label_data

    def foriegn_size_data(self, size):
        """Return label data for foreign sizes."""
        size_list = [
            "{}: {}".format(size[0], size[1])
            for size in size.get_sizes()
            if len(size[1]) > 0
        ]
        return [" ".join(_) for _ in self.split_list(size_list, 3)]


class TestProductPDFLabel(BaseProductPDFLabelView):
    """View to create a PDF of labels generated from test data."""

    def get(self, *args, **kwargs):
        """Return test label PDF."""
        return self.create_label_response(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Prevent POST requests."""
        return http.HttpResponseNotAllowed(["GET"])

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


class AddressLabelForm(LabelmakerUserMixin, TemplateView):
    """View for the address label creation form."""

    template_name = "labelmaker/address_label_form.html"


class AddressLabelPDF(BasePDFLabelView):
    """View for address label PDF creation."""

    label_format = labeler.AddressLabelFormat
    label_sheet = labeler.ThermalAddressLabel4x6Sheet

    def get_label_data(self, *args, **kwargs):
        """Return list containing lists of lines of text for each label."""
        text = self.request.POST.get("label_text")
        return self.parse_label_data(text)

    def parse_label_data(self, text):
        """Return the label text as a list of lines."""
        if text is None:
            raise http.Http404
        return [text.split("\r\n")]


class SmallLabelForm(LabelmakerUserMixin, TemplateView):
    """View for the small label creation form."""

    template_name = "labelmaker/small_label_form.html"


class SmallLabelPDF(BasePDFLabelView):
    """View for address label PDF creation."""

    label_format = labeler.SmallLabelFormat
    label_sheet = labeler.STW046025PO

    def get_label_data(self, *args, **kwargs):
        """Return list containing lists of lines of text for each label."""
        text = [_ for _ in self.request.POST.getlist("label_text") if _]
        quantities = [int(_) for _ in self.request.POST.getlist("quantity")]
        return self.parse_label_data(text, quantities)

    def parse_label_data(self, text, quantities):
        """Return the label text as a list of lines."""
        data = []
        for i, line in enumerate(text):
            label_text = line.split("\r\n")
            for _ in range(quantities[i]):
                data.append(label_text)
        return data
