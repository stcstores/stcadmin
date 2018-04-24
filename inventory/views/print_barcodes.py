"""Views for Barcode Label creation."""

import json

import labeler
from ccapi import CCAPI
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView

from .views import InventoryUserMixin


class PrintBarcodeLabels(InventoryUserMixin, TemplateView):
    """View for barcode label page."""

    template_name = 'inventory/print_barcodes.html'

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        product_range = CCAPI.get_range(
            self.kwargs.get('range_id'))
        for product in product_range.products:
            product.option_text = product.full_name.replace(
                '{} - '.format(product.name), '')
        context['product_range'] = product_range
        return context


class BarcodePDF(InventoryUserMixin, View):
    """Create PDF document containing barcode labels."""

    def post(self, *args, **kwargs):
        """Handle POST HTTP request."""
        data = self.get_label_data()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="labels.pdf"'
        label_format = labeler.BarcodeLabelFormat
        sheet = labeler.STW046025PO(label_format=label_format)
        canvas = sheet.generate_PDF_from_data(data)
        canvas._filename = response
        canvas.save()
        return response

    def get_label_data(self):
        """Get data for barcode labels."""
        json_data = self.request.POST.get('data')
        data = json.loads(json_data)
        barcode_data = []
        for product in data:
            for i in range(int(product['quantity'])):
                barcode_data.append(
                    (product['barcode'], product['option_text']))
        return barcode_data
