"""Views for the reference app."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class Index(LoginRequiredMixin, TemplateView):
    """View for the reference landing page."""

    template_name = 'reference/index.html'
