"""Models for the ITD app."""
import csv
import io
from datetime import timedelta

from ccapi import CCAPI
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from solo.models import SingletonModel

from itd.tasks import clear_manifest_files, close_manifest
from shipping.models import Country, ShippingRule


def itd_order_id(order_id):
    """Return an order ID fomatted for ITD."""
    return f"CCPpackord({order_id})"


class ITDConfig(SingletonModel):
    """Model for ITD Manifest settings."""

    shipping_rules = models.ManyToManyField(ShippingRule)

    class Meta:
        """Meta class for ITDConfig."""

        verbose_name = "ITD Configuration"


class ITDManifestManager(models.Manager):
    """Model Manager for the ITDManifest model."""

    DAYS_SINCE_DISPATCH = 7

    def create_manifest(self):
        """Create a new manifest."""
        manifest = self.create()
        close_manifest.delay(manifest.id)
        return manifest

    def close_manifest(self, manifest_id):
        """Close a manifest."""
        manifest = super().get_queryset().get(id=manifest_id)
        manifest.close()

    def _recent_order_ids(self):
        orders_since = timezone.now() - timedelta(self.DAYS_SINCE_DISPATCH)
        return ITDOrder.objects.filter(
            manifest__created_at__gte=orders_since
        ).values_list("order_id", flat=True)

    def get_current_orders(self):
        """Return orders to be manifested."""
        config = ITDConfig.objects.get()
        existing_orders = self._recent_order_ids()
        shipping_rule_ids = [_.rule_ID for _ in config.shipping_rules.all()]
        orders = []
        for rule_id in shipping_rule_ids:
            rule_orders = CCAPI.get_orders_for_dispatch(
                order_type=1,
                number_of_days=ITDManifest.objects.DAYS_SINCE_DISPATCH,
                courier_rule_id=rule_id,
            )
            rule_orders = [
                _ for _ in rule_orders if str(_.order_id) not in existing_orders
            ]
            orders.extend(rule_orders)
        return orders

    def ready_to_create(self):
        """Return True if a manifest can be created, otherwise False."""
        return (
            not self.get_queryset()
            .filter(Q(status=ITDManifest.GENERATING) | Q(status=ITDManifest.OPEN))
            .exists()
        )


class ITDManifest(models.Model):
    """Model for ITD manifests."""

    OPEN = "open"
    CLOSED = "closed"
    GENERATING = "generating"
    ERROR = "error"
    COMPLETE = "complete"

    STATUS_CHOICES = (
        (OPEN, "Open"),
        (CLOSED, "Closed"),
        (GENERATING, "Generating Manifest File"),
        (ERROR, "Error"),
    )

    PERSIST_FILES = timedelta(minutes=30)

    created_at = models.DateTimeField(auto_now_add=True)
    last_generated_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    manifest_file = models.FileField(upload_to="itd/manifests/", null=True)

    objects = ITDManifestManager()

    class Meta:
        """Meta class for ITDConfig."""

        verbose_name = "ITD Manifest"
        verbose_name_plural = "ITD Manifests"
        ordering = ("-created_at",)

    def close(self):
        """Create a new manifest."""
        if self.status != self.OPEN:
            raise ValueError("Cannot close a manifest that is not open.")
        self.status = self.GENERATING
        self.save()
        try:
            self._generate_manifest()
        except Exception as e:
            self.status = self.ERROR
            self.save()
            raise e
        else:
            self.status = self.CLOSED
            self.save()
        finally:
            clear_manifest_files.apply_async(
                args=[self.id], eta=timezone.now() + self.PERSIST_FILES
            )

    def _generate_manifest(self):
        cc_orders = self.__class__.objects.get_current_orders()
        with transaction.atomic():
            for cc_order in cc_orders:
                ITDOrder.objects.create_from_dispatch_order(
                    manifest=self, cc_order=cc_order
                )
        manifest_file = _ITDManifestFile.create(cc_orders)
        self.manifest_file.save(
            "ITD_Manifest.csv", ContentFile(manifest_file.getvalue())
        )

    def clear_files(self):
        """Delete manifest files."""
        self.manifest_file.delete(save=True)


class ITDOrderManager(models.Manager):
    """Model manager for the ITDOrder model."""

    @transaction.atomic
    def create_from_dispatch_order(self, manifest, cc_order):
        """Create an ITDOrder object from Cloud Commerce dispatch information."""
        order = self.create(
            manifest=manifest,
            order_id=cc_order.order_id,
            customer_id=cc_order.customer_id,
        )
        for product in cc_order.products:
            ITDProduct.objects.create_from_dispatch(order=order, cc_product=product)
        return order


class ITDOrder(models.Model):
    """Model for orders sent by ITD."""

    order_id = models.CharField(max_length=20, unique=True)
    customer_id = models.CharField(max_length=20)
    manifest = models.ForeignKey(ITDManifest, on_delete=models.CASCADE)

    objects = ITDOrderManager()

    class Meta:
        """Meta class for ITDConfig."""

        verbose_name = "ITD Manifest Order"
        verbose_name_plural = "ITD Manifest Orders"

    def itd_id(self):
        """Return the order ID as presented to ITD."""
        return itd_order_id(self.order_id)

    def get_cc_order(self):
        """Return the details of the order from Cloud Commerce."""
        return CCAPI.get_orders_for_dispatch(order_type=1, search_term=self.order_id)[0]


class ITDProductManager(models.Manager):
    """Model manager for the ITDProduct model."""

    def create_from_dispatch(self, order, cc_product):
        """Create an ITDProduct object from Cloud Commerce product information."""
        return self.create(
            order=order,
            sku=cc_product.sku,
            name=cc_product.product_name,
            price=int(cc_product.price * 100),
            weight=int(cc_product.per_item_weight),
            quantity=cc_product.quantity,
        )


class ITDProduct(models.Model):
    """Model for products sent by ITD."""

    order = models.ForeignKey(ITDOrder, on_delete=models.CASCADE)
    sku = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    weight = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    objects = ITDProductManager()

    class Meta:
        """Meta class for ITDConfig."""

        verbose_name = "ITD Manifest Product"
        verbose_name_plural = "ITD Manifest Products"


class _ITDManifestFile:
    class Address:
        def __init__(self, order_address_string):
            parts = order_address_string.split(",")
            self.city, self.region, self.postcode = parts[-3:]
            lines = "".join(parts[:-3])
            if "#" in lines:
                lines = lines[: lines.index("#")]
            if "\t" in lines:
                tab_index = lines.index("\t")
                self.line_1 = lines[:tab_index]
                self.line_2 = lines[tab_index + 1 :]
            else:
                self.line_1 = lines
                self.line_2 = ""
            if "(" in self.postcode:
                self.postcode = self.postcode[: self.postcode.index("(")]
            self.line_1 = self.line_1.strip()
            self.line_2 = self.line_2.strip()
            self.city = self.city.strip()
            self.region = self.region.strip()
            self.postcode = self.postcode.strip()

    @classmethod
    def create(cls, orders):
        rows = []
        for order in orders:
            rows.extend(cls.get_order_rows(order))
        return cls.create_csv(rows)

    @classmethod
    def get_order_rows(cls, order):
        rows = []
        address = cls.Address(order.delilvery_address)
        country = cls.get_country(order)
        order_id = itd_order_id(order.order_id)
        first_name, second_name = cls.get_names(order.delivery_name)
        for product in order.products:
            weight = product.per_item_weight / 1000
            product_row = [
                first_name,
                second_name,
                address.line_1,
                address.line_2,
                address.city,
                address.region,
                country,
                address.postcode,
                order_id,
                product.product_name,
                product.sku,
                f"{weight:.2f}",
                order.total_gross_gbp,
            ]
            rows.extend([product_row] * product.quantity)
        return rows

    @classmethod
    def get_country(cls, order):
        return Country.objects.get(country_ID=order.delivery_country_code).name

    @classmethod
    def get_names(cls, order_name):
        order_name = order_name.strip()
        try:
            space_index = order_name.index(" ")
        except ValueError:
            return "First name", order_name.strip()
        else:
            return order_name[:space_index].strip(), order_name[space_index:].strip()

    @classmethod
    def create_csv(cls, rows):
        stream = io.StringIO()
        writer = csv.writer(stream, delimiter=",")
        writer.writerows(rows)
        return stream
