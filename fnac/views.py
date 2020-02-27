"""Views for the fnac app."""

from django.views.generic.base import TemplateView

from home.views import UserInGroupMixin


class FnacUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the print audit group."""

    groups = ["fnac"]


class Index(FnacUserMixin, TemplateView):
    """Index view for the fnac app."""

    template_name = "fnac/index.html"
