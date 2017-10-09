from django.db import models
from django.db.models import Q
from django.utils.timezone import now


class DestinationZone(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)

    class Meta:
        ordering = ('name', )

    def safe_name(self):
        return self.name.lower().replace(' ', '_')

    def __str__(self):
        return str(self.name)


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
    zone = models.ForeignKey(DestinationZone, blank=True, null=True)
    valid_spring_destination = models.BooleanField(
        default=True, verbose_name='Valid Spring Destination')

    objects = models.Manager()
    incomplete = IncompleteCountryManager()

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return str(self.name)


class ManifestedOrder(models.Model):

    order_id = models.CharField(max_length=10)
    service_code = models.CharField(max_length=3)
    country = models.ForeignKey(CloudCommerceCountryID)
    manifest_time = models.DateTimeField(default=now)

    @classmethod
    def order_ids(cls):
        return set(o.order_id for o in cls.objects.all())

    def __str__(self):
        return str(self.order_id)
