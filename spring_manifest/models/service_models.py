"""Models for manifest services."""

from django.db import models

from .cloud_commerce_shipping_rule import CloudCommerceShippingRule
from .manifest_type_model import ManifestType


class EnabledServices(models.Manager):
    """Manager for in use shipping services."""

    def get_queryset(self):
        """Return valid, enabled shipping services."""
        return super().get_queryset().filter(
            enabled=True, shipping_rules__isnull=False).distinct()


class ManifestService(models.Model):
    """Model for manifested shipping services."""

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    manifest_type = models.ForeignKey(
        ManifestType, on_delete=models.SET_NULL, blank=True, null=True)
    shipping_rules = models.ManyToManyField(
        CloudCommerceShippingRule, blank=True)
    enabled = models.BooleanField(default=True)

    objects = models.Manager()
    enabled_services = EnabledServices()

    class Meta:
        """Meta class for the Service model."""

        verbose_name = 'Manifest Service'
        verbose_name_plural = 'Manifest Services'

    def __str__(self):
        return self.name

    def shipping_rule_IDs(self):
        """Return a list of shipping rule IDs as a string."""
        shipping_rules = self.shipping_rules.all()
        if len(shipping_rules) > 0:
            return ', '.join([str(rule) for rule in shipping_rules])
        else:
            return 'No shipping rules selected.'


class SecuredMailService(models.Model):
    """Models for Secured Mail shipping services."""

    shipping_service = models.ForeignKey(
        ManifestService, on_delete=models.SET_NULL, null=True, blank=True)
    on_item_advice = models.BooleanField(default=False)
    on_manifest = models.BooleanField(default=False)
    on_docket = models.BooleanField(default=False)
    docket_service = models.CharField(max_length=255, blank=True, null=True)
    format = models.CharField(max_length=255)
    proof_of_delivery = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        """Meta class for the Service model."""

        verbose_name = 'Secured Mail Service'
        verbose_name_plural = 'Secured Mail Services'

    def __str__(self):
        if self.shipping_service is not None:
            return self.shipping_service.name
        else:
            return 'Secured Mail Service Not Matched To Manifest Service'
