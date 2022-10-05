"""Models for managing Linnworks Shipping."""

from django.db import models

from shipping.models import ShippingService


class LinnworksShippingService(models.Model):
    """Model for Linnworks shipping services."""

    name = models.CharField(max_length=255)
    shipping_service = models.ForeignKey(
        ShippingService,
        on_delete=models.PROTECT,
        related_name="linnworks_shipping_services",
    )

    class Meta:
        """Meta class for Linnworks Shipping Service."""

        verbose_name = "Linnworks Shipping Service"
        verbose_name_plural = "Linnworks Shipping Services"
