"""Views for the tracking app."""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View

from orders.forms import TrackingWarningFilter
from tracking import models


class TrackingHistory(TemplateView):
    """View for order tracking history."""

    template_name = "tracking/tracking_history.html"

    def get_context_data(self, *args, **kwargs):
        """Return Tracked Package and Tracking Events."""
        context = super().get_context_data(*args, **kwargs)
        tracking_number = self.kwargs.get("tracking_number")
        package = models.TrackedPackage.objects.get(tracking_number=tracking_number)
        events = package.tracking_event.all()
        context["package"] = package
        context["events"] = events
        return context


class UpdateTracking(View):
    """View for updating tracking information for a tracking number."""

    def get(self, *args, **kwargs):
        """Update tracking information for a tracking number."""
        tracking_number = self.kwargs.get("tracking_number")
        package = models.TrackingAPI.get_tracking_by_tracking_number(tracking_number)
        models.TrackingAPI.add_package_tracking(package)
        return HttpResponse("ok")


class TrackingWarnings(TemplateView):
    """View for listing overdue packages."""

    template_name = "tracking/tracking_warnings.html"

    def post(self, *args, **kwargs):
        """Allow POST requests."""
        return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        form = TrackingWarningFilter(self.request.POST)
        if form.is_valid():
            context["packages"] = models.TrackingStatus.get_tracking_warnings(
                filters=form.filter_kwargs
            )
        return context


@method_decorator(csrf_exempt, name="dispatch")
class UpdateTrackedPackage(View):
    """View for updating tracked packages via AJAX."""

    def post(self, *args, **kwargs):
        """Update tracked package information."""
        package_pk = self.request.POST["package_id"]
        package = get_object_or_404(models.TrackedPackage, pk=package_pk)
        if "carrier_contacted" in self.request.POST:
            package.carrier_contacted = self.request.POST["carrier_contacted"] == "true"
        if "notes" in self.request.POST:
            package.notes = self.request.POST["notes"]
        package.save()
        return HttpResponse("ok")
