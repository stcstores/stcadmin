from django.db import models
from django.db.models import Q

from .destination_zone_model import DestinationZone


class IncompleteCountryManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            valid_spring_destination=True).filter(
                Q(iso_code='') | Q(zone=None))


class CloudCommerceCountryID(models.Model):

    name = models.CharField(max_length=50)
    cc_id = models.IntegerField()
    iso_code = models.CharField(
        max_length=3, blank=True, null=True, verbose_name='ISO Code')
    zone = models.ForeignKey(
        DestinationZone, blank=True, null=True, on_delete=models.CASCADE)
    valid_spring_destination = models.BooleanField(
        default=True, verbose_name='Valid Spring Destination')
    currency_code = models.CharField(max_length=4, blank=True, null=True)

    objects = models.Manager()
    incomplete = IncompleteCountryManager()

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return str(self.name)

    def is_valid_destination(self):
        return all((self.iso_code, self.zone, self.valid_spring_destination))
