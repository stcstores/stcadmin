"""Views for the tracking app."""

from django.http import HttpResponse
from django.views.generic import TemplateView, View

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

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["packages"] = models.TrackingStatus.get_tracking_warnings()
        for package in context["packages"]:
            try:
                package.latest_event = package.tracking_event.latest("timestamp")
            except models.TrackingEvent.DoesNotExist:
                package.latest_event = None
        return context
