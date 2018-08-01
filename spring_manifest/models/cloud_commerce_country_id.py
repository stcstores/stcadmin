"""CloudCommerceCountryID model."""

from django.db import models
from django.db.models import Q

from .secured_mail_destination_model import SecuredMailDestination


class IncompleteCountryManager(models.Manager):
    """Manager for countries with missing information."""

    def get_queryset(self):
        """Return queryset of countries with missing information."""
        return super().get_queryset().filter(Q(iso_code='') | Q(zone=None))


class CloudCommerceCountryID(models.Model):
    """Model for destination countries."""

    name = models.CharField(max_length=50)
    cc_id = models.IntegerField()
    iso_code = models.CharField(
        max_length=3, blank=True, null=True, verbose_name='ISO Code')
    secured_mail_destination = models.ForeignKey(
        SecuredMailDestination,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    currency_code = models.CharField(max_length=4, blank=True, null=True)

    objects = models.Manager()
    incomplete = IncompleteCountryManager()

    class Meta:
        """Meta class for CloudCommerceCountryID."""

        verbose_name = 'Cloud Commerce Country ID'
        verbose_name_plural = 'Cloud Commerce Country IDs'
        ordering = ('name', )

    def __str__(self):
        return str(self.name)
