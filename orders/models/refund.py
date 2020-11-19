"""Model for refund tracking."""


from collections import defaultdict

from django.db import models, transaction
from django.shortcuts import reverse
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from polymorphic.models import PolymorphicModel

from inventory.models import Supplier
from shipping.models import Provider

from .order import Order
from .product_sale import ProductSale


class Refund(PolymorphicModel):
    """Model for refund requests."""

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    closed = models.BooleanField(default=False)
    images_required = False
    created_at = models.DateTimeField(auto_now_add=True)
    is_partial = models.BooleanField(default=False)

    def get_absolute_url(self):
        """Return the URL for this refund."""
        return reverse("orders:refund", kwargs={"pk": self.pk})

    def reason(self):
        """Return the reason for the refund."""
        return self._meta.verbose_name.title().replace(" Refund", "")

    @classmethod
    def from_order(cls, order, products):
        """
        Create a refund.

        args:
            order (orders.models.Order): The order to which the refund belongs.
            products (tulple(orders.models.ProductSale, int)): A lost of tuples of
                ProductSale objects to which the refund applies and the quantity of that
                product to which it applies.

        """
        with transaction.atomic():
            refund = cls(order=order)
            refund.save()
            for product_sale, quantity in products:
                ProductRefund(
                    refund=refund, product=product_sale, quantity=quantity
                ).save()
            return [refund]


class ContactRefund(Refund):
    """Model for refunds with status tracking."""

    contact_contacted = models.BooleanField(default=False)
    refund_accepted = models.BooleanField(blank=True, null=True)
    refund_amount = models.PositiveIntegerField(blank=True, null=True)


class SupplierRefund(ContactRefund):
    """Model for refunds from suppliers."""

    contact_name = "Supplier"
    supplier = models.ForeignKey(
        Supplier, null=True, blank=True, on_delete=models.PROTECT
    )
    images_required = True

    @classmethod
    def from_order(cls, order, products):
        """
        Create a refund for each supplier in an order.

        args:
            order (orders.models.Order): The order to which the refund belongs.
            products (tulple(orders.models.ProductSale, int)): A lost of tuples of
                ProductSale objects to which the refund applies and the quantity of that
                product to which it applies.

        """
        with transaction.atomic():
            refunds = []
            supplier_products = defaultdict(list)
            for product_sale, quantity in products:
                supplier_products[product_sale.supplier].append(
                    (product_sale, quantity)
                )
            for supplier, products in supplier_products.items():
                refund = cls(order=order, supplier=supplier)
                refunds.append(refund)
                refund.save()
                for product_sale, quantity in products:
                    ProductRefund(
                        refund=refund, product=product_sale, quantity=quantity
                    ).save()
        return refunds


class CourierRefund(ContactRefund):
    """Model for refunds from couriers."""

    contact_name = "Logistics Partner"
    courier = models.ForeignKey(
        Provider, null=True, blank=True, on_delete=models.PROTECT
    )

    @classmethod
    def from_order(cls, order, products):
        """
        Create a refund.

        args:
            order (orders.models.Order): The order to which the refund belongs.
            products (tulple(orders.models.ProductSale, int)): A lost of tuples of
                ProductSale objects to which the refund applies and the quantity of that
                product to which it applies.

        returns:
            A list of refunds created.

        """
        with transaction.atomic():
            courier = order.shipping_rule.courier_service.courier.courier_type.provider
            refund = cls(order=order, courier=courier)
            refund.save()
            for product_sale, quantity in products:
                ProductRefund(
                    refund=refund, product=product_sale, quantity=quantity
                ).save()
        return [refund]


class BreakageRefund(SupplierRefund):
    """Model for refunds lost in the post."""

    pass


class PackingMistakeRefund(Refund):
    """Model for refunds lost in the post."""

    pass


class LinkingMistakeRefund(Refund):
    """Model for refunds lost in the post."""

    pass


class LostInPostRefund(CourierRefund):
    """Model for refunds lost in the post."""

    returned = models.BooleanField(default=False)


class DemicRefund(SupplierRefund):
    """Model for refunds lost in the post."""

    pass


class ProductRefund(models.Model):
    """Model for products requiring a refund."""

    refund = models.ForeignKey(
        Refund, on_delete=models.CASCADE, related_name="products"
    )
    product = models.ForeignKey(ProductSale, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)


def image_path(instance, filename):
    """Return the path to which refund images will be saved."""
    path = f"refunds/images/{instance.refund.id}/"
    if instance.product_refund is not None:
        path += f"{instance.product_refund.id}/"
    path += filename
    return path


def thumb_path(instance, filename):
    """Return the path to which refund images will be saved."""
    path = f"refunds/thumbs/{instance.refund.id}/"
    if instance.product_refund is not None:
        path += f"{instance.product_refund.id}/"
    path += filename
    return path


class RefundImage(models.Model):
    """Model for images of refunds."""

    THUMB_SIZE = 200

    refund = models.ForeignKey(Refund, on_delete=models.CASCADE)
    product_refund = models.ForeignKey(
        ProductRefund, blank=True, null=True, on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to=image_path, height_field="image_height", width_field="image_width"
    )
    thumbnail = ProcessedImageField(
        upload_to=thumb_path,
        processors=[ResizeToFit(THUMB_SIZE, THUMB_SIZE)],
        format="JPEG",
        options={"quality": 60},
        height_field="thumb_height",
        width_field="thumb_width",
    )
    image_height = models.PositiveIntegerField()
    image_width = models.PositiveIntegerField()
    thumb_height = models.PositiveIntegerField()
    thumb_width = models.PositiveIntegerField()
