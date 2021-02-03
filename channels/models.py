"""Models for the channels app."""

import json

from ccapi import CCAPI, NewOrderItem
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from solo.models import SingletonModel


class DefaultContact(SingletonModel):
    """Model for default contact information."""

    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return "Default Order Contact"

    class Meta:
        """Meta class for DefaultContact."""

        verbose_name = "Default Order Contact"


class ActiveChannels(models.Manager):
    """Manager for active channels."""

    def get_queryset(self):
        """Return a querset of active channels."""
        return super().get_queryset().filter(inactive=False)


class Channel(models.Model):
    """Model for Cloud Commerce channels."""

    name = models.CharField(max_length=200)
    channel_id = models.CharField(max_length=10)
    inactive = models.BooleanField(default=False)

    objects = models.Manager()
    active = ActiveChannels()

    def __str__(self):
        return self.name


class CreatedOrder(models.Model):
    """Model for storing created orders."""

    channel = models.ForeignKey(Channel, on_delete=models.PROTECT)
    customer_id = models.CharField(max_length=20)
    order_id = models.CharField(max_length=20)
    billing_address_id = models.CharField(max_length=20)
    delivery_address_id = models.CharField(max_length=20)
    invoice_id = models.CharField(max_length=20)
    price = models.FloatField()
    shipping_price = models.FloatField()
    total_to_pay = models.FloatField()

    def get_absolute_url(self):
        """Return the absolute url of the order."""
        return reverse("channels:created_order", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Created Order {self.order_id}"

    def customer_url(self):
        """Return a link to the Customer on Cloud Commerce."""
        return f"https://{settings.CC_DOMAIN}/Admin/Customer.aspx?CustID={self.customer_id}"

    def order_url(self):
        """Return a link to the Order on Cloud Commerce."""
        return (
            f"https://{settings.CC_DOMAIN}/Admin/OrderDetails.aspx?"
            f"OrderID={self.order_id}&CustomerID={self.customer_id}"
        )


class CreatedOrderProduct(models.Model):
    """Model for storing products associated with an order."""

    order = models.ForeignKey(CreatedOrder, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=20)
    quantity = models.PositiveSmallIntegerField()
    item_price = models.FloatField()

    def total_price(self):
        """Return the total price for the item."""
        return self.item_price * self.quantity


class CreateOrder:
    """Create an order in Cloud Commerce."""

    BILLING_ADDRESS = "Billing"
    DELIVERY_ADDRESS = "Delivery"

    def __init__(self, data):
        """Create an order from channels.forms.CreateOrder data."""
        self.default_contact = DefaultContact.get_solo()
        self.customer_name = data["customer_name"]
        self.first_name = self.customer_name.split(" ")[0]
        self.last_name = " ".join(self.customer_name.split(" ")[1:])
        self.address_1 = data["address_line_1"]
        self.address_2 = data["address_line_2"]
        self.town = data["town"]
        self.contact_email = data["email"] or self.default_contact.email
        self.phone_number = data["phone_number"] or self.default_contact.phone
        self.post_code = data["post_code"]
        self.country = data["country"]
        self.channel_id = data["channel"]
        self.shipping_price = data["shipping_price"]
        self.products = []
        for product in json.loads(data["basket"]):
            product_id = product["product_id"]
            price = float(product["price"])
            quantity = product["quantity"]
            self.products.append(
                NewOrderItem(
                    product_id=product_id,
                    item_net=price,
                    item_gross=price,
                    total_net=price * quantity,
                    total_gross=price * quantity,
                    quantity=quantity,
                )
            )
        self.price = sum((product.total_gross for product in self.products))
        self.to_pay = self.price + self.shipping_price

    def create_customer(self):
        """Create the customer."""
        self.customer_id = CCAPI.add_customer(
            customer_name=self.customer_name,
            address_1=self.address_1,
            address_2=self.address_2,
            country=self.country,
            post_code=self.post_code,
            selling_channel_id=self.channel_id,
            contact_email=self.contact_email,
            contact_phone=self.phone_number,
        )

    def make_address(self, address_type):
        """Add an address to the customer."""
        return CCAPI.add_address(
            customer_id=self.customer_id,
            address_type=address_type,
            first_name=self.first_name,
            last_name=self.last_name,
            address_1=self.address_1,
            address_2=self.address_2,
            post_code=self.post_code,
            town=self.town,
            country=self.country,
            email=self.contact_email,
            telephone_number=self.phone_number,
        )

    def create_billing_address(self):
        """Set the billing address."""
        self.billing_address_id = self.make_address(self.BILLING_ADDRESS)

    def create_delivery_address(self):
        """Set the delivery address."""
        self.delivery_address_id = self.make_address(self.DELIVERY_ADDRESS)

    def create_order(self):
        """Create the order."""
        order = CCAPI.create_order(
            customer_id=self.customer_id,
            items=self.products,
            delivery_address_id=self.delivery_address_id,
            billing_address_id=self.billing_address_id,
            channel_id=self.channel_id,
            carriage_net=self.shipping_price,
            carriage_vat="0",
            total_net=self.price,
            total_gross=self.price,
        )
        self.order_id = order.order_id
        self.invoice_id = order.invoice_id

    def create_payment(self):
        """Mark the order paid."""
        payment_created = CCAPI.insert_payment(
            customer_id=self.customer_id,
            invoice_id=self.invoice_id,
            amount=self.to_pay,
            channel_id=self.channel_id,
        )
        if payment_created is not True:
            raise Exception(f"Order not paid {self.order_id}")

    def create(self):
        """Create a new customer and order."""
        self.create_customer()
        self.create_billing_address()
        self.create_delivery_address()
        self.create_order()
        self.create_payment()
        return self.save_order()

    def save_order(self):
        """Add order details to the database."""
        order = CreatedOrder(
            channel=Channel.objects.get(channel_id=self.channel_id),
            customer_id=self.customer_id,
            order_id=self.order_id,
            billing_address_id=self.billing_address_id,
            delivery_address_id=self.billing_address_id,
            invoice_id=self.invoice_id,
            price=self.price,
            shipping_price=self.shipping_price,
            total_to_pay=self.to_pay,
        )
        order.save()
        for product in self.products:
            CreatedOrderProduct(
                product_id=product.product_id,
                quantity=product.quantity,
                item_price=product.item_net,
                order=order,
            ).save()
        return order
