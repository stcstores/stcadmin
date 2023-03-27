"""Views for the UPS Manifestor application."""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from fba import models


class BaseShippingAPIView(View):
    """Base view for API requests."""

    def authenticate(self):
        """Ensure the request data contains a valid token."""
        token = self.request.POST.get("token")
        expected_token = models.ShipmentConfig.get_solo().token
        return token == expected_token

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """Handle the request."""
        if self.authenticate() is False:
            return HttpResponse("Unauthorized", status=401)
        else:
            return super().dispatch(request, *args, **kwargs)


class CurrentShipments(BaseShippingAPIView):
    """View for providing currently open shipments."""

    def get_shipments(self):
        """Return a queryset of current shipments."""
        return models.FBAShipmentOrder.objects.filter(
            export__isnull=True, is_on_hold=False, shipment_package__isnull=False
        ).distinct()

    def shipment_data(self, shipment):
        """Return information about current shipments as a dict."""
        weight = shipment.weight_kg()
        value = shipment.value()
        return {
            "id": shipment.id,
            "order_number": shipment.order_number(),
            "description": shipment.description(),
            "destination": shipment.destination.name,
            "user": str(shipment.user),
            "package_count": shipment.shipment_package.count(),
            "weight": round(weight, 2) if weight else "N/A",
            "value": f"£{shipment.value()/100:.2f}" if value else "N/A",
        }

    def post(self, request, *args, **kwargs):
        """Return information about current shipments."""
        shipments = self.get_shipments()
        data = {"shipments": [self.shipment_data(shipment) for shipment in shipments]}
        return JsonResponse(data)


class ShipmentExports(BaseShippingAPIView):
    """View for providing information about existing shipment exports."""

    EXPORT_LIMIT = 20

    def get_exports(self):
        """Return a queryset of shipment exports."""
        qs = models.FBAShipmentExport.objects.all().order_by("-created_at")
        return qs[: self.EXPORT_LIMIT]

    def export_data(self, export):
        """Return information about shipment exports as a dict."""
        return {
            "id": export.id,
            "order_numbers": export.order_numbers(),
            "description": export.description(),
            "destinations": export.destinations(),
            "shipment_count": export.shipment_count(),
            "package_count": export.package_count(),
            "created_at": export.created_at.strftime("%d %b %Y %H:%M"),
        }

    def post(self, request, *args, **kwargs):
        """Return information about recent shipment exports."""
        exports = self.get_exports()
        data = {"exports": [self.export_data(export) for export in exports]}
        return JsonResponse(data)


class DownloadShipmentFile(BaseShippingAPIView):
    """View for providing UPS shipment files."""

    def post(self, request, *args, **kwargs):
        """Return an HTTP response containing the requested shipment file."""
        export_id = request.POST["export_id"]
        export = get_object_or_404(models.FBAShipmentExport, id=export_id)
        contents = export.generate_export_file()
        response = HttpResponse(contents, content_type="text/csv")
        filename = f"FBA_Shipment_File_{export.created_at.strftime('%Y-%m-%d')}.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class DownloadAddressFile(BaseShippingAPIView):
    """View for providing UPS address files."""

    def post(self, request, *args, **kwargs):
        """Return an HTTP response containing the requested address file."""
        export_id = request.POST["export_id"]
        export = get_object_or_404(models.FBAShipmentExport, id=export_id)
        contents = export.generate_address_file()
        response = HttpResponse(contents, content_type="text/csv")
        filename = "FBA_Shipment_ADDRESS.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class CloseShipment(BaseShippingAPIView):
    """View for processing currently open shipments."""

    def post(self, request, *args, **kwargs):
        """Close open shipments and return the ID of the created export."""
        shipment_id = request.POST["shipment_id"]
        shipment_order = get_object_or_404(models.FBAShipmentOrder, pk=shipment_id)
        export = shipment_order.close_shipment_order()
        return JsonResponse({"export_id": export.id})
