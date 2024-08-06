"""Models for managing Parcelhub API shipments."""

from django.conf import settings
from django.db import models
from django.utils import timezone
from parcelhubapi import CreateShipmentRequest, ParcelhubAPISession, ShipmentRequest
from solo.models import SingletonModel


class ParcelhubAPIConfig(SingletonModel):
    """Model for Parcelhub API configuration."""

    service_id = models.CharField(max_length=20, blank=True, null=True)
    customer_id = models.CharField(max_length=20, blank=True, null=True)
    provider_id = models.CharField(max_length=20, blank=True, null=True)

    ready_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)

    collection_contact_name = models.CharField(max_length=50, blank=True, null=True)
    collection_company_name = models.CharField(max_length=20, blank=True, null=True)
    collection_phone = models.CharField(max_length=20, blank=True, null=True)
    collection_address_1 = models.CharField(max_length=255, blank=True, null=True)
    collection_address_2 = models.CharField(max_length=255, blank=True, null=True)
    collection_city = models.CharField(max_length=50, blank=True, null=True)
    collection_area = models.CharField(max_length=50, blank=True, null=True)
    collection_postcode = models.CharField(max_length=50, blank=True, null=True)
    collection_country = models.CharField(max_length=3, blank=True, null=True)
    collection_email = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        """Meta class for ParcelhubAPIConfig."""

        verbose_name = "Parcelhub API Config"


class ParcelhubShipment(models.Model):
    """Model for recording Parcelhub shipments."""

    shipment_order = models.OneToOneField(
        "FBAShipmentOrder", on_delete=models.PROTECT, related_name="parcelhub_shipment"
    )
    shipment_id = models.CharField(max_length=255)
    courier_tracking_number = models.CharField(max_length=255)
    parcelhub_tracking_number = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        """Meta class for ParcelhubShipment."""

        verbose_name = "Parcelhub Shipment"
        verbose_name_plural = "Parcelhub Shipments"
        ordering = ("-created_at",)

    class ParcelhubShipmentManager(models.Manager):
        """Manager for the ParcelhubShipment model."""

        def create_shipment(self, shipment_order):
            """Create a Parcelhub API shipment."""
            if self.filter(shipment_order=shipment_order).exists():
                raise Exception("Shipment already filed.")
            shipment_creator = self._ParcelhubAPIShipmentCreator(
                shipment_order=shipment_order
            )
            shipment_info = shipment_creator.create_shipment()
            record = self.model(
                shipment_order=shipment_order,
                shipment_id=shipment_info.shipment_id,
                courier_tracking_number=shipment_info.courier_tracking_number,
                parcelhub_tracking_number=shipment_info.parcelhub_tracking_number,
            )
            record.save()
            return record

        class _ParcelhubAPIShipmentCreator:
            """Class for creating Parcelhub API shipments."""

            def __init__(self, shipment_order):
                """
                Create a Parcelhub API shipment.

                Args:
                    shipment_order (fba.models.fba_order.FBAShipmentOrder): The order to create.
                """
                self.shipment_order = shipment_order

            def create_shipment(self):
                """Create a Parcelhub API shipment."""
                self.config = ParcelhubAPIConfig.get_solo()
                self.session = ParcelhubAPISession(
                    username=settings.PARCELHUB_API_USERNAME,
                    password=settings.PARCELHUB_API_PASSWORD,
                    account_id=settings.PARCELHUB_API_ACCOUNT_ID,
                )
                self.session.authorise_session()
                self.request_data = ShipmentRequest(
                    session=self.session,
                    reference=self.shipment_order.order_number,
                    description="Goods",
                    currency="GBP",
                )
                self.set_service_info()
                self.set_collection_details()
                self.set_collection_address()
                self.set_delivery_address()
                self.set_customs_declaration()
                self.add_packages()
                return self.make_create_shipment_request()

            def set_service_info(self):
                """Set the request data's shipping service information."""
                self.request_data.set_service_info(
                    service_id=self.config.service_id,
                    customer_id=self.config.customer_id,
                    provider_id=self.config.provider_id,
                )

            def set_collection_details(self):
                """Set the request data's collection information."""
                self.request_data.set_collection_details(
                    collection_date=timezone.now().date(),
                    ready_time=self.config.ready_time,
                    close_time=self.config.close_time,
                )

            def set_collection_address(self):
                """Set the request data's collection address."""
                self.request_data.set_collection_address(
                    contact_name=self.config.collection_contact_name,
                    company_name=self.config.collection_company_name,
                    phone=self.config.collection_phone,
                    address_1=self.config.collection_address_1,
                    address_2=self.config.collection_address_2,
                    city=self.config.collection_city,
                    area=self.config.collection_area,
                    postcode=self.config.collection_postcode,
                    country=self.config.collection_country,
                    address_type=self.request_data.BUSINESS,
                    email=self.config.collection_email,
                )

            def set_delivery_address(self):
                """Set the request data's delivery address."""
                destination = self.shipment_order.destination
                self.request_data.set_delivery_address(
                    contact_name=destination.recipient_name,
                    company_name=destination.name,
                    phone=destination.contact_telephone,
                    address_1=destination.address_line_1,
                    address_2=destination.address_line_2,
                    city=destination.city,
                    area=destination.state,
                    postcode=destination.postcode,
                    country=destination.country_iso,
                    address_type=self.request_data.BUSINESS,
                    email=self.config.collection_email,
                )

            def set_customs_declaration(self):
                """Set the request data's customs declaration."""
                self.request_data.set_customs_declaration(
                    terms=ShipmentRequest.UNAPID,
                    postal_charges=0,
                    category="Sold",
                    category_explanation="",
                    value=self.shipment_order.value,
                    insurance_value=0,
                    other_value=0,
                )

            def add_packages(self):
                """Add packages to the request data."""
                for package in self.shipment_order.shipment_package.all():
                    request_package = self.add_package(package)
                    for item in package.shipment_item.all():
                        self.add_item(request_package=request_package, item=item)

            def add_package(self, package):
                """Add a package to the request data."""
                return self.request_data.add_package(
                    package_type=self.request_data.PALLET,
                    length=package.length_cm,
                    height=package.height_cm,
                    width=package.width_cm,
                    weight=round(package.weight_kg, 2),
                    value=self.as_currency(package.value),
                    contents="Goods",
                )

            def add_item(self, request_package, item):
                """Add an item to the request data."""
                request_package.add_item(
                    sku=item.sku,
                    description=item.description[:35],
                    product_type=item.description[:35],
                    value=self.as_currency(item.value),
                    quantity=item.quantity,
                    weight=round(item.weight_kg, 2),
                    country_of_origin="GB",
                    hr_code=item.hr_code,
                )

            def make_create_shipment_request(self):
                """Register the shipment with the Parcelhub API."""
                return CreateShipmentRequest(session=self.session).call(
                    shipment_request=self.request_data
                )

            def as_currency(self, value):
                """Return pence as pounds and pence."""
                return f"{(value / 100):.2f}"

    objects = ParcelhubShipmentManager()

    def __str__(self):
        return f"{self.shipment_order.order_number} - {self.courier_tracking_number}"


class ParcelhubShipmentFiling(models.Model):
    """Model for attemps to file Parcelhub shipments."""

    shipment_order = shipment_order = models.ForeignKey(
        "FBAShipmentOrder",
        on_delete=models.CASCADE,
        related_name="parcelhub_shipment_filings",
    )
    started_at = models.DateTimeField(default=timezone.now, editable=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    shipment = models.OneToOneField(
        ParcelhubShipment,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="shipment_filings",
    )

    class Meta:
        """Meta class for ParcelhubShipmentFiling."""

        verbose_name = "Parcelhub Shipment Filing"
        verbose_name_plural = "Parcelhub Shipment Filings"
        ordering = ("-started_at",)

    class ParcelhubShipmentFilingManager(models.Manager):
        """Manager for ParcelhubShipmentFiling."""

        def create_filing(self, shipment_order):
            """Create a new filing object."""
            return self.create(shipment_order=shipment_order)

    objects = ParcelhubShipmentFilingManager()

    def __str__(self):
        return f"Parcelhub Filing: {self.shipment_order.order_number} - {self.status()}"

    def status(self):
        """Return a string descriptin the status of the filing."""
        if self.error_message:
            return "ERROR"
        elif self.shipment is not None and self.completed_at is not None:
            return "COMPLETE"
        elif self.completed_at is None:
            return "IN PROGRESS"
        raise ValueError("Invalid Parcelhub shipment fileing status")

    def set_error(self, error_message):
        """Set the filing as complete with error."""
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()

    def set_complete(self, shipment):
        """Set the filing as complete without error."""
        self.completed_at = timezone.now()
        self.shipment = shipment
        self.save()
