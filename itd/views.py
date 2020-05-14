"""Views for the ITD app."""

from django.http import HttpResponse
from django.views.generic import TemplateView, View

from itd import models
from spring_manifest.views import SpringUserMixin


class ITDManifest(SpringUserMixin, TemplateView):
    """View for ITD manifests."""

    template_name = "itd/manifests.html"


class ITDManifestList(SpringUserMixin, TemplateView):
    """View for the ITD manifest list display."""

    template_name = "itd/manifest_list.html"
    MANIFESTS_TO_DISPLAY = 8

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["manifests"] = models.ITDManifest.objects.all()[
            : self.MANIFESTS_TO_DISPLAY
        ]
        context["ready_to_create"] = models.ITDManifest.objects.ready_to_create()
        return context


class CreateITDManifest(SpringUserMixin, View):
    """View for triggering the creation of a new ITD Manifest."""

    def get(*args, **kwargs):
        """Create a new ITD manifest."""
        try:
            models.ITDManifest.objects.create_manifest()
        except Exception:
            return HttpResponse(status=500)
        else:
            return HttpResponse("done")
