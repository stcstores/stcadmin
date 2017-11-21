import pytz
from ccapi import CCAPI
from django.db import models
from django.utils.timezone import is_naive

from .cloud_commerce_country_id import CloudCommerceCountryID
from .spring_manifest_model import SpringManifest


class SpringOrderManager(models.Manager):

    def create_from_order(self, order, service=None, manifest=None):
        return self.create(
            order_id=str(order.order_id),
            customer_name=order.delivery_name,
            date_recieved=order.date_recieved,
            dispatch_date=order.dispatch_date,
            country=CloudCommerceCountryID._base_manager.get(
                cc_id=order.delivery_country_code),
            product_count=len(order.products),
            manifest=manifest,
            service=service)

    def order_ids(self):
        return set(o.order_id for o in self.get_queryset().all())


class UnManifestedManager(SpringOrderManager):

    def get_queryset(self):
        return super().get_queryset().filter(
            manifest__isnull=True, canceled=False)


class ManifestedManager(SpringOrderManager):

    def get_queryset(self):
        return super().get_queryset().filter(manifest__isnull=False)


class FiledManager(ManifestedManager):

    def get_queryset(self):
        return super().get_queryset().filter(
            manifest__time_filed__isnull=False)


class UnFiledManager(ManifestedManager):

    def get_queryset(self):
        return super().get_queryset().filter(
            manifest__time_filed__isnull=True, canceled=False)


class CanceledOrdersManager(SpringOrderManager):

    def get_queryset(self):
        return super().get_queryset().filter(canceled=True)


class SpringOrder(models.Model):

    PACKET = 'PAK'
    PARCEL = 'PAR'
    TRACKED = 'PAT'
    SERVICE_CHOICES = (
        (PARCEL, 'Parcel'), (PACKET, 'Packet'), (TRACKED, 'Tracked'))

    MANIFEST_SELECTION = {
        PACKET: SpringManifest.UNTRACKED,
        PARCEL: SpringManifest.TRACKED,
        TRACKED:  SpringManifest.TRACKED,
    }


    order_id = models.CharField(max_length=10, unique=True)
    customer_name = models.CharField(max_length=100)
    date_recieved = models.DateTimeField()
    dispatch_date = models.DateTimeField()
    country = models.ForeignKey(
        CloudCommerceCountryID, on_delete=models.CASCADE)
    product_count = models.PositiveIntegerField()
    package_count = models.PositiveIntegerField(default=1)
    manifest = models.ForeignKey(
        SpringManifest, blank=True, null=True, on_delete=models.CASCADE)
    service = models.CharField(max_length=3, choices=SERVICE_CHOICES)
    canceled = models.BooleanField(default=False)

    objects = SpringOrderManager()
    manifested = ManifestedManager()
    unmanifested = UnManifestedManager()
    filed = FiledManager()
    unfiled = UnFiledManager()
    canceled_orders = CanceledOrdersManager()

    def __str__(self):
        return self.order_id

    def save(self, *args, **kwargs):
        self.date_recieved = self.localise_datetime(self.date_recieved)
        self.dispatch_date = self.localise_datetime(self.dispatch_date)
        if self.canceled:
            self.manifest = None
        super().save(*args, **kwargs)

    def localise_datetime(self, date_input):
        if date_input is not None and is_naive(date_input):
            tz = pytz.timezone('Europe/London')
            date_input = date_input.replace(tzinfo=tz)
        return date_input

    def add_to_manifest(self, manifest):
        self.manifest = manifest
        self.save()

    def get_order_data(self):
        return CCAPI.get_orders_for_dispatch(
            order_type=1, number_of_days=30, id_list=[self.order_id])[0]
