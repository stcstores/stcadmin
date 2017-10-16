import pytz
from django.db import models
from django.db.models import Q
from django.utils.timezone import is_naive, now


class DestinationZone(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    format_code = models.CharField(
        max_length=1, blank=True, null=True, default=None)

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


class SpringManifest(models.Model):

    time_manifested = models.DateTimeField(default=now)


class SpringOrder(models.Model):

    order_id = models.CharField(max_length=10, unique=True)
    customer_name = models.CharField(max_length=100)
    date_recieved = models.DateTimeField()
    dispatch_date = models.DateTimeField()
    manifest = models.ForeignKey(SpringManifest, blank=True, null=True)

    @classmethod
    def create_from_order(cls, order):
        return cls._base_manager.create(
            order_id=str(order.order_id),
            customer_name=order.delivery_name,
            date_recieved=order.date_recieved,
            dispatch_date=order.dispatch_date)

    def save(self, *args, **kwargs):
        self.date_recieved = self.localise_datetime(self.date_recieved)
        self.dispatch_date = self.localise_datetime(self.dispatch_date)
        super().save(*args, **kwargs)

    def localise_datetime(self, date_input):
        if is_naive(date_input):
            tz = pytz.timezone('Europe/London')
            return date_input.replace(tzinfo=tz)

    @classmethod
    def order_ids(cls):
        return set(o.order_id for o in cls.objects.all())

    def __str__(self):
        return str(self.order_id)
