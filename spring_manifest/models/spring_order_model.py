"""SpringOrder model."""

import pytz
from ccapi import CCAPI
from django.db import models
from django.db.models import Sum
from django.utils.timezone import is_naive

from .cloud_commerce_country_id import CloudCommerceCountryID
from .spring_manifest_model import SpringManifest


class SpringOrderManager(models.Manager):
    """Manager for SpringOrder model."""

    def order_ids(self):
        """Return set of order IDs for orders in queryset."""
        return set(o.order_id for o in self.get_queryset().all())

    def items(self):
        """Return items included in order."""
        from .spring_item_model import SpringItem
        return SpringItem._base_manager.filter(
            package__order__in=self.get_queryset())


class UnManifestedManager(SpringOrderManager):
    """Manager for orders not on any manifest."""

    def get_queryset(self):
        """Return queryset of orders not on any manifest."""
        return super().get_queryset().filter(
            manifest__isnull=True, canceled=False)


class ManifestedManager(SpringOrderManager):
    """Manager for orders on manifests."""

    def get_queryset(self):
        """Return queryset of orders on manifests."""
        return super().get_queryset().filter(manifest__isnull=False)


class FiledManager(ManifestedManager):
    """Manager for orders on filed manifests."""

    def get_queryset(self):
        """Return queryset of orders on filed manifests."""
        return super().get_queryset().filter(
            manifest__time_filed__isnull=False)


class UnFiledManager(ManifestedManager):
    """Manager for orders on unfiled manifests."""

    def get_queryset(self):
        """Return queryset of orders on unfiled manifests."""
        return super().get_queryset().filter(
            manifest__time_filed__isnull=True, canceled=False)


class CanceledOrdersManager(SpringOrderManager):
    """Manager for canceled orders."""

    def get_queryset(self):
        """Return qureryset of canceled orders."""
        return super().get_queryset().filter(canceled=True)


class SpringOrder(models.Model):
    """Model for orders on manifests."""

    PACKET = 'PAK'
    PARCEL = 'PAR'
    TRACKED = 'PAT'
    SIGNED = 'PAP'
    SM_INT_UNTRACKED = 'SMIU'
    SM_INT_TRACKED = 'SMIT'
    SERVICE_CHOICES = (
        (PARCEL, 'Spring Parcel'), (PACKET, 'Spring Packet'),
        (TRACKED, 'Spring Tracked'), (SIGNED, 'Spring Signed'),
        (SM_INT_UNTRACKED, 'Secure Mail International Untracked'),
        (SM_INT_TRACKED, 'Secure Mail International Tracked'))

    MANIFEST_SELECTION = {
        PACKET: SpringManifest.UNTRACKED,
        PARCEL: SpringManifest.TRACKED,
        TRACKED: SpringManifest.TRACKED,
        SIGNED: SpringManifest.TRACKED,
        SM_INT_TRACKED: SpringManifest.SECURED_MAIL,
        SM_INT_UNTRACKED: SpringManifest.SECURED_MAIL,
    }

    order_id = models.CharField(max_length=10, unique=True)
    customer_name = models.CharField(max_length=100)
    date_recieved = models.DateTimeField()
    dispatch_date = models.DateTimeField()
    country = models.ForeignKey(
        CloudCommerceCountryID, on_delete=models.CASCADE)
    manifest = models.ForeignKey(
        SpringManifest, blank=True, null=True, on_delete=models.CASCADE)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    canceled = models.BooleanField(default=False)

    objects = SpringOrderManager()
    manifested = ManifestedManager()
    unmanifested = UnManifestedManager()
    filed = FiledManager()
    unfiled = UnFiledManager()
    canceled_orders = CanceledOrdersManager()

    class Meta:
        """Meta class for SpringOrder."""

        verbose_name = 'Spring Order'
        verbose_name_plural = 'Spring Orders'

    def __str__(self):
        return self.order_id

    def save(self, *args, **kwargs):
        """Localise datetimes and unset manifest if order is canceled."""
        self.date_recieved = self.localise_datetime(self.date_recieved)
        self.dispatch_date = self.localise_datetime(self.dispatch_date)
        if self.canceled:
            self.manifest = None
        super().save(*args, **kwargs)

    def localise_datetime(self, date_input):
        """Localise datetime."""
        if date_input is not None and is_naive(date_input):
            tz = pytz.timezone('Europe/London')
            date_input = date_input.replace(tzinfo=tz)
        return date_input

    def add_to_manifest(self, manifest):
        """Add order to manifest."""
        self.manifest = manifest
        self.save()

    def get_order_data(self):
        """Return information about order."""
        return CCAPI.get_orders_for_dispatch(
            order_type=1, number_of_days=30, id_list=[self.order_id])[0]

    def items(self):
        """Return queryset of items in order."""
        from .spring_item_model import SpringItem
        return SpringItem._base_manager.filter(package__order=self)

    def get_cc_item_dict(self):
        """Return product IDs and quantities according to Cloud Commerce."""
        order = self.get_order_data()
        return {int(p.product_id): p.quantity for p in order.products}

    def get_item_dict(self):
        """Return product IDs and quantities according to database."""
        quantities = {}
        for package in self.springpackage_set.all():
            for item in package.springitem_set.all():
                if item.item_id not in quantities:
                    quantities[item.item_id] = 0
                quantities[item.item_id] += item.quantity
        return quantities

    def check_items(self):
        """Return True products and quantities match Cloud Commerce."""
        return self.get_item_dict() == self.get_cc_item_dict()

    def item_quantity(self):
        """Return number of items associated with order."""
        from .spring_item_model import SpringItem
        return SpringItem.objects.filter(package__order=self).aggregate(
            Sum('quantity'))['quantity__sum']

    def update_packages(self, package_data):
        """Update package information associated with this order."""
        from .spring_package_model import SpringPackage
        from .spring_item_model import SpringItem
        self.clear_packages()
        for package_number, package in enumerate(package_data):
            package_obj = SpringPackage(
                order=self, package_number=package_number)
            package_obj.save()
            for item_data in package:
                item_id, quantity = item_data
                item = SpringItem(
                    package=package_obj, item_id=item_id,
                    quantity=quantity)
                item.save()
