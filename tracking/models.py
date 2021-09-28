"""Models for the tracking app."""

import datetime
import re

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from scurri import ScurriAPI

from orders.models import Order as CloudCommerceOrder
from shipping.models import Region as ShippingRegion


class TrackingAPI:
    """Methods for retrieving information from the Scurri API."""

    def with_scurri_api(func):
        """Authenticate with Scurri API and return ScurriAPI object."""

        def scurri_api_wrapper(*args, **kwargs):
            scurri_api = ScurriAPI(staging=False)
            scurri_api.auth(
                username=settings.SCURRI_USERNAME, password=settings.SCURRI_PASSWORD
            )
            return func(scurri_api, *args, **kwargs)

        return scurri_api_wrapper

    @staticmethod
    @with_scurri_api
    def get_tracking_information(scurri_api):
        """Return currernt Surri tracking information."""
        return scurri_api.get_trackings()

    @staticmethod
    @with_scurri_api
    def find_carrier(scurri_api, carrier_slug):
        """Return carrier information for a carrier slug."""
        return scurri_api.get_carrier(carrier_slug=carrier_slug)

    @staticmethod
    @with_scurri_api
    def get_tracking_by_tracking_number(scurri_api, tracking_number):
        """Return tracking information for a package by tracking number."""
        carrier = TrackingCarrier.objects.find_carrier_for_tracking_number(
            tracking_number
        )
        return scurri_api.get_tracking_by_tracking_number(
            carrier_slug=carrier.slug, tracking_number=tracking_number
        )

    @classmethod
    def update_tracking_information(cls):
        """Retrieve current tracking information and update database."""
        trackings = TrackingAPI.get_tracking_information()
        for package_tracking in trackings:
            cls.add_package_tracking(package_tracking)

    @classmethod
    def add_package_tracking(cls, package_tracking):
        """Add a package to the database."""
        with transaction.atomic():
            TrackingCarrier.objects.get_or_create_by_carrier_slug(
                package_tracking.carrier_slug
            )
            package = TrackedPackage.objects.get_or_create_by_scurri_id(
                package_tracking.id, package_tracking
            )
            for event in package_tracking.events:
                cls.add_tracking_event(package=package, event=event)

    @staticmethod
    @with_scurri_api
    def get_package_by_id(scuri_api, package_id):
        """Request a package by package ID."""
        return scuri_api.get_tracking_by_package_id(package_id)

    @classmethod
    def add_tracking_event(cls, package, event):
        """Add an event to the database."""
        event, created = TrackingEvent.objects.update_or_create(
            event_id=event.id,
            defaults={
                "package": package,
                "status": event.status,
                "carrier_code": event.carrier_code,
                "description": event.description,
                "timestamp": timezone.make_aware(event.timestamp),
                "location": event.location,
            },
        )


class TrackingCarrierManager(models.Manager):
    """Manager for the TrackingCarrier model."""

    def get_or_create_by_carrier_slug(self, carrier_slug):
        """Return the Carrier matching carrier_slug, create if it does not exist."""
        try:
            carrier = self.get(slug=carrier_slug)
        except self.model.DoesNotExist:
            carrier_info = TrackingAPI.find_carrier(carrier_slug=carrier_slug)
            carrier = self.create_from_scurri(carrier_info)
        return carrier

    def create_from_scurri(self, carrier_info):
        """Create a new Carrier object from Scurri API information."""
        obj = self.create(slug=carrier_info.slug, name=carrier_info.name)
        return obj

    def find_carrier_for_tracking_number(self, tracking_number):
        """Return the apropriate carrier for a tracking number."""
        carriers = self.filter(tracking_number_match__isnull=False)
        for carrier in carriers:
            if re.search(carrier.tracking_number_match, tracking_number):
                return carrier
        raise ValueError(f'Carrier not found for tracking number "{tracking_number}".')


class TrackingCarrier(models.Model):
    """Model for tracked package carriers."""

    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    tracking_number_match = models.CharField(max_length=255, blank=True)

    objects = TrackingCarrierManager()

    class Meta:
        """Meta clas for TrackingCarrier."""

        verbose_name = "Tracking Carrier"
        verbose_name_plural = "Tracking Carriers"

    def __str__(self):
        return self.name


class TrackedPackageManager(models.Manager):
    """Manager for the TrackedPackage model."""

    def get_or_create_by_scurri_id(self, scurri_id, package_info):
        """Return a package matching a scurri ID or create it if it does not exist."""
        try:
            tracked_package = self.get(scurri_id=scurri_id)
        except self.model.DoesNotExist:
            tracked_package = self.create_from_scurri(package_info)
        return tracked_package

    def create_from_scurri(self, package_info):
        """Create a tracked package from information provided by the Scurri API."""
        try:
            order = CloudCommerceOrder.objects.get(
                tracking_number=package_info.tracking_number
            )
        except CloudCommerceOrder.DoesNotExist:
            order = None
        obj = self.create(
            carrier=TrackingCarrier.objects.get(slug=package_info.carrier_slug),
            scurri_id=package_info.id,
            tracking_number=package_info.tracking_number,
            created_at=package_info.created_at,
            order=order,
        )
        return obj


class TrackedPackage(models.Model):
    """Model for recording tracked packages."""

    scurri_id = models.CharField(max_length=255)
    carrier = models.ForeignKey(
        TrackingCarrier, related_name="tracked_package", on_delete=models.PROTECT
    )
    tracking_number = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    order = models.ForeignKey(
        CloudCommerceOrder,
        related_name="tracked_package",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    objects = TrackedPackageManager()

    class Meta:
        """Meta clas for TrackedPackage."""

        verbose_name = "Tracked Package"
        verbose_name_plural = "Tracked Packages"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.carrier.name}: {self.scurri_id} - {self.tracking_number}"

    def update_tracking(self):
        """Update tracking events for this package."""
        package_info = TrackingAPI.get_package_by_id(self.scurri_id)
        for event in package_info.events:
            TrackingAPI.add_tracking_event(package=self, event=event)
        if self.order is None:
            try:
                order = CloudCommerceOrder.objects.get(
                    tracking_number=self.tracking_number
                )
            except CloudCommerceOrder.DoesNotExist:
                pass
            else:
                self.order = order
                self.save()


class TrackingEvent(models.Model):
    """Model for recording tracking events."""

    ATTEMPTED_DELIVERY = "ATTEMPTED_DELIVERY"
    UNKNOWN = "UNKNOWN"
    MANIFESTED = "MANIFESTED"
    IN_TRANSIT = "IN_TRANSIT"
    EXCEPTION = "EXCEPTION"
    DELIVERED = "DELIVERED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"

    STATUS_CHOICES = (
        (MANIFESTED, MANIFESTED),
        (IN_TRANSIT, IN_TRANSIT),
        (OUT_FOR_DELIVERY, OUT_FOR_DELIVERY),
        (ATTEMPTED_DELIVERY, ATTEMPTED_DELIVERY),
        (DELIVERED, DELIVERED),
        (EXCEPTION, EXCEPTION),
        (UNKNOWN, UNKNOWN),
    )

    event_id = models.CharField(max_length=255)
    package = models.ForeignKey(
        TrackedPackage, related_name="tracking_event", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    carrier_code = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=255)

    class Meta:
        """Meta clas for TrackingEvent."""

        verbose_name = "Tracking Event"
        verbose_name_plural = "Tracking Events"
        ordering = ("-timestamp",)


class TrackingStatus:
    """Find overdue packages."""

    ORDER_CHECK_MIN_DAYS_OLD = 2
    ORDER_CHECK_MAX_DAYS_OLD = 10

    @classmethod
    def get_tracking_warnings(cls, filters):
        """Return a list of overdue packages."""
        packages = []
        for region in ShippingRegion.objects.all():
            dispatched_after = timezone.now() - datetime.timedelta(
                days=region.flag_if_not_delivered_by_days
            )
            region_packages = cls.get_packages_for_region(
                region=region, dispatched_after=dispatched_after, filters=filters
            )
            cls.add_latest_event_attribute_to_packages(region_packages)
            packages.extend(region_packages)
            packages.sort(key=lambda x: x.order.dispatched_at)
        return packages

    @classmethod
    def get_packages_for_region(cls, region, dispatched_after, filters):
        """Return a queryset of packages with tracking warnings for a region."""
        region_packages = (
            TrackedPackage.objects.select_related("order")
            .select_related("order__country")
            .select_related("carrier")
            .prefetch_related("tracking_event")
            .filter(
                order__dispatched_at__lte=dispatched_after,
                order__country__region=region,
            )
            .exclude(tracking_event__status=TrackingEvent.DELIVERED)
            .exclude(tracking_event__description="Secure delivery - To household")
            .exclude(carrier__slug="landmark")  # Remove when landmark works
            .filter(**filters)
        )
        return region_packages

    @classmethod
    def add_latest_event_attribute_to_packages(cls, packages):
        """Add the latest tracking event as an attribute to packages."""
        for package in packages:
            try:
                package.latest_event = package.tracking_event.first()
            except TrackingEvent.DoesNotExist:
                package.latest_event = None

    @classmethod
    def get_min_max_order_dates(cls):
        """Return the dates between which orders should be updated."""
        now = timezone.now()
        dispatched_after = now - datetime.timedelta(days=cls.ORDER_CHECK_MIN_DAYS_OLD)
        dispatched_before = now - datetime.timedelta(days=cls.ORDER_CHECK_MAX_DAYS_OLD)
        return dispatched_before, dispatched_after

    @classmethod
    def get_recent_orders(cls):
        """Return a queryset of orders that may be overdue."""
        dispatched_before, dispatched_after = cls.get_min_max_order_dates()
        return CloudCommerceOrder.objects.filter(
            dispatched_at__gte=dispatched_before,
            dispatched_at__lte=dispatched_after,
            tracking_number__isnull=False,
        ).prefetch_related("tracked_package")

    @classmethod
    def update_tracking(cls):
        """Update tracking information for potentially overdue packages."""
        orders = cls.get_recent_orders()
        calls = 0
        for order in orders:
            try:
                package = order.tracked_package.get()
            except TrackedPackage.DoesNotExist:
                try:
                    package_info = TrackingAPI.get_tracking_by_tracking_number(
                        order.tracking_number
                    )
                    calls += 1
                except Exception:
                    continue
                else:
                    package = TrackedPackage.objects.create_from_scurri(package_info)
            else:
                try:
                    package.update_tracking()
                except Exception:
                    continue
