"""Views for the Wowcher app."""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView, TemplateView

from home.views import UserInGroupMixin
from wowcher import models
from wowcher.wowcher_management import ProofOfDeliveryFile, RedemptionFile


class WowcherUserMixin(UserInGroupMixin):
    """View mixin ensuring user has permissions for this app."""

    groups = ["wowcher"]


class Orders(WowcherUserMixin, TemplateView):
    """View for wowcher index page."""

    template_name = "wowcher/orders.html"

    def get_context_data(self, *args, **kwargs):
        """Add undispatched orders to the context."""
        context = super().get_context_data(*args, **kwargs)
        context["orders"] = models.WowcherOrder.to_dispatch.all()
        context["stock_alerts"] = models.WowcherStockLevelCheck.stock_alerts.all()
        return context


class BaseWowcherFile(WowcherUserMixin, TemplateView):
    """Base view for wowcher file pages."""

    template_name = "wowcher/download_file.html"

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["orders"] = self.order_manager.all()
        context["previous_file"] = self.get_previous_file()
        if context["previous_file"] is not None:
            context["download_previous_url"] = reverse_lazy(
                self.donwload_URL_pattern, args=[context["previous_file"].id]
            )
        context["file_name"] = self.file_name
        context["create_url"] = reverse_lazy(self.create_URL_pattern)
        return context

    def get_previous_file(self):
        """Return the most recent proof of delivery file if it exists, otherwise return None."""
        try:
            return self.model.objects.latest("time_created")

        except self.mdoel.DoesNotExist:
            return None


class GetRedemptionFile(BaseWowcherFile):
    """View for the Wowcher Redemption file page."""

    order_manager = models.WowcherOrder.for_redemption_file
    model = models.WowcherRedemptionFile
    donwload_URL_pattern = "wowcher:download_redemption_file"
    create_URL_pattern = "wowcher:create_redemption_file"
    file_name = "redemption"


class ProofOfDelivery(BaseWowcherFile):
    """View for the Wowcher Proof of Delivery file page."""

    order_manager = models.WowcherOrder.for_proof_of_delivery_file
    model = models.WowcherProofOfDeliveryFile
    donwload_URL_pattern = "wowcher:download_proof_of_delivery_file"
    create_URL_pattern = "wowcher:create_proof_of_delivery_file"
    file_name = "proof of delivery"


class BaseCreateFileView(WowcherUserMixin, RedirectView):
    """Base view for creating Wowcher files."""

    def get_redirect_url(self, *args, **kwargs):
        """Return a redirect to download the new file."""
        new_file = self.file_class.new()
        return reverse_lazy(self.download_URL_pattern, args=[new_file.id])


class CreateRedemptionFile(BaseCreateFileView):
    """View for creating a new redemption file."""

    file_class = RedemptionFile
    download_URL_pattern = "wowcher:download_redemption_file"


class CreateProofOfDeliveryFile(BaseCreateFileView):
    """View for creating a new Proof of Delivery file."""

    file_class = ProofOfDeliveryFile
    download_URL_pattern = "wowcher:download_proof_of_delivery_file"


class DownloadRedemptionFile(WowcherUserMixin, RedirectView):
    """View for downloading a Redemption file."""

    def get(self, *args, **kwargs):
        """Return a download of a Redemption file."""
        redemption_file = get_object_or_404(
            models.WowcherRedemptionFile, id=self.kwargs["file_ID"]
        )
        filename, file_contents = RedemptionFile.contents(redemption_file)
        response = HttpResponse(file_contents, content_type="application/csv")
        response["Content-Disposition"] = f"attachment;filename={filename}"
        return response


class DownloadProofOfDeliveryFile(WowcherUserMixin, RedirectView):
    """View for downloading a Proof of Delivery file."""

    def get(self, *args, **kwargs):
        """Return a download of a Proof of Delivery file."""
        proof_of_delivery_file = get_object_or_404(
            models.WowcherProofOfDeliveryFile, id=self.kwargs["file_ID"]
        )
        filename, file_contents = ProofOfDeliveryFile.contents(proof_of_delivery_file)
        response = HttpResponse(file_contents, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = f"attachment;filename={filename}"
        return response


class CancelOrder(WowcherUserMixin, RedirectView):
    """Cancel a Wowcher order and redirect to the orders page."""

    def get_redirect_url(self, *args, **kwargs):
        """Cancel a Wowcher order and redirect to the orders page."""
        order = get_object_or_404(models.WowcherOrder, id=self.kwargs["order_ID"])
        order.canceled = True
        order.save()
        return reverse_lazy("wowcher:orders")


class HideStockAlert(WowcherUserMixin, RedirectView):
    """Hide an item's stock alerts and redirect to the order page."""

    def get_redirect_url(self, *args, **kwargs):
        """Hide an item's stock alerts and redirect to the order page."""
        item = get_object_or_404(models.WowcherItem, id=self.kwargs["item_ID"])
        item.hide_stock_alert = True
        item.save()
        return reverse_lazy("wowcher:orders")
