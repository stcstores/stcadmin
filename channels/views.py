"""Views for the channels app."""

from django.views.generic.base import TemplateView

from home.views import UserInGroupMixin


class ChannelsUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the channels group."""

    groups = ["channels"]


class Index(ChannelsUserMixin, TemplateView):
    """Main view for the orders app."""

    template_name = "channels/index.html"
