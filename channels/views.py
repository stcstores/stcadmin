"""Views for the channels app."""

from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from channels import forms, models
from home.views import UserInGroupMixin
from shipping.models import Country


class ChannelsUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the channels group."""

    groups = ["channels"]


class Index(ChannelsUserMixin, TemplateView):
    """Main view for the orders app."""

    template_name = "channels/index.html"


class CreateOrderChannelSelect(ChannelsUserMixin, TemplateView):
    """View for selecting a channel to create an order for."""

    template_name = "channels/create_order_channel_select.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["channels"] = models.Channel.active.all()
        return context


class CreateOrder(ChannelsUserMixin, FormView):
    """View for creating orders."""

    form_class = forms.CreateOrder
    template_name = "channels/new_order.html"

    def get_form_kwargs(self):
        """Set form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["channel"] = models.Channel.objects.get(pk=self.kwargs.get("channel_pk"))
        return kwargs

    def form_valid(self, form):
        """Create the order."""
        data = form.cleaned_data
        data["channel"] = form.channel.channel_id
        self.order_object = models.CreateOrder(data).create()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.values_list("name", flat=True)
        return context

    def get_success_url(self):
        """Redirect after successful submission."""
        return self.order_object.get_absolute_url()


class CreatedOrder(ChannelsUserMixin, TemplateView):
    """View for created orders."""

    template_name = "channels/created_order.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["order"] = models.CreatedOrder.objects.get(pk=self.kwargs.get("pk"))
        return context
