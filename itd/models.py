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

from itd.tasks import clear_manifest_files, close_manifest, regenerate_manifest
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

    def regenerate_manifest(self, manifest_id):
        """Regenerate a manifest file."""
        manifest = super().get_queryset().get(id=manifest_id)
        manifest.regenerate()

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
                order_type=0, number_of_days=0, courier_rule_id=rule_id,
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
    NO_ORDERS = "no_orders"

    STATUS_CHOICES = (
        (OPEN, "Open"),
        (CLOSED, "Closed"),
        (GENERATING, "Generating Manifest File"),
        (ERROR, "Error"),
        (NO_ORDERS, "No Orders"),
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
        self._check_status_before_closing()
        self._set_status(self.GENERATING)
        cc_orders = self._get_cc_orders()
        if len(cc_orders) > 0:
            self._add_orders_to_db(cc_orders)
            self._generate_manifest(cc_orders)
            self._set_status(self.CLOSED)
            self._set_clear_files()
        else:
            self._set_status(self.NO_ORDERS)

    def regenerate(self):
        """Recreate the manifest file."""
        self._check_status_before_regenerating()
        self._set_status(self.GENERATING)
        orders = self._reaquire_orders()
        self._generate_manifest(orders)
        self._set_clear_files()
        self.last_generated_at = timezone.now()
        self._set_status(self.CLOSED)

    def regenerate_async(self):
        """Regenerate the manifest file asynchronously."""
        regenerate_manifest.delay(self.id)

    def _reaquire_orders(self):
        cc_orders = []
        try:
            for order in self.itdorder_set.all():
                results = CCAPI.get_orders_for_dispatch(search_term=order.order_id)
                cc_orders.extend(results)
        except Exception as e:
            self._set_status(self.ERROR)
            raise e
        else:
            return cc_orders

    def _set_clear_files(self):
        clear_manifest_files.apply_async(
            args=[self.id], eta=timezone.now() + self.PERSIST_FILES
        )

    def _check_status_before_closing(self):
        if self.status != self.OPEN:
            raise ValueError("Cannot close a manifest that is not open.")

    def _check_status_before_regenerating(self):
        if self.status != self.CLOSED:
            raise ValueError("Cannot regenerate a manifest that is not closed.")

    @transaction.atomic
    def _add_orders_to_db(self, cc_orders):
        for cc_order in cc_orders:
            ITDOrder.objects.create_from_dispatch_order(
                manifest=self, cc_order=cc_order
            )

    def _generate_manifest(self, cc_orders):
        manifest_file = _ITDManifestFile.create(cc_orders)
        self.manifest_file.save(
            "ITD_Manifest.csv", ContentFile(manifest_file.getvalue())
        )

    def _set_status(self, status):
        self.status = status
        self.save()

    def _get_cc_orders(self):
        try:
            return self.__class__.objects.get_current_orders()
        except Exception as e:
            self._set_status(self.ERROR)
            raise e

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
            self.line_1, self.line_2 = self.get_address_lines("".join(parts[:-3]))
            if "(" in self.postcode:
                self.postcode = self.postcode[: self.postcode.index("(")].strip()
            self.line_1 = self.line_1.strip()
            self.line_2 = self.line_2.strip()
            self.city = self.city.strip()
            self.region = self.region.strip() or self.city
            self.postcode = self.postcode.strip()

        def strip_hash(self, address_string):
            if "#" in address_string:
                address_string = address_string[: address_string.index("#")]
            return address_string

        def get_address_lines(self, address_string):
            address_string = self.strip_hash(address_string)
            line_1, line_2 = self.split_address_lines(address_string)
            line_1, line_2 = self.fix_address_length(line_1, line_2)
            return line_1.strip(), line_2.strip()

        def split_address_lines(self, address_string):
            if "\t" in address_string:
                tab_index = address_string.index("\t")
                line_1 = address_string[:tab_index].strip()
                line_2 = address_string[tab_index + 1 :].strip()
            else:
                line_1 = address_string.strip()
                line_2 = ""
            return line_1.strip(), line_2.strip()

        def fix_address_length(self, line_1, line_2):
            while len(line_1) > 35:
                try:
                    space_index = line_1.rindex(" ")
                except ValueError:
                    space_index = 35
                line_2 = " ".join((line_1[space_index:], line_2))
                line_1 = line_1[:space_index]
            return line_1, line_2

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
