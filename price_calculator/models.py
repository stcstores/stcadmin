"""Models for price_calculator app."""

from django.db import models
from django.db.models import Q

from inventory.models import PackageType
from shipping.models import Country, ShippingPrice, ShippingService


class CountryChannelFee(models.Model):
    """Model for storing the minimum channel fee for a country."""

    country = models.OneToOneField(Country, on_delete=models.CASCADE)
    min_channel_fee = models.PositiveIntegerField()

    class Meta:
        """Meta class for CountryChannelFee."""

        verbose_name = "Country Channel Fee"
        verbose_name_plural = "Country Channel Fees"


class ChannelFee(models.Model):
    """Model for channel fees."""

    name = models.CharField(max_length=50, unique=True)
    fee_percentage = models.FloatField()
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="channel_fees"
    )
    ordering = models.PositiveSmallIntegerField(default=100)

    class Meta:
        """Meta class for ChannelFee."""

        verbose_name = "Channel Fee"
        verbose_name_plural = "Channel Fees"
        ordering = ("ordering",)

    def __str__(self):
        return self.name


class Channel(models.Model):
    """Model for channels."""

    name = models.CharField(max_length=50, unique=True)
    ordering = models.PositiveSmallIntegerField(default=100)

    class Meta:
        """Meta class for Channel."""

        verbose_name = "Channel"
        verbose_name_plural = "Channel"
        ordering = ("ordering",)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    """Model for types of packaging."""

    name = models.CharField(max_length=50, unique=True)
    package_types = models.ManyToManyField(PackageType, blank=True)

    class Meta:
        """Meta class for ProductType."""

        verbose_name = "Product Type"
        verbose_name_plural = "Product Types"

    def __str__(self):
        return self.name

    def package_type_string(self):
        """Return a list of package types as a string."""
        return ", ".join([_.name for _ in self.package_types.all()])

    def description(self):
        """Return the description of the first associated package type."""
        try:
            return self.package_types.all()[0].description
        except IndexError:
            return ""


class VATRate(models.Model):
    """Model for VAT rates."""

    name = models.CharField(max_length=50)
    cc_id = models.PositiveSmallIntegerField()
    percentage = models.PositiveSmallIntegerField()
    ordering = models.PositiveSmallIntegerField(default=100)

    class Meta:
        """Meta class for VATRate."""

        verbose_name = "VAT Rate"
        verbose_name_plural = "VAT Rates"
        ordering = ("ordering",)

    def __str__(self):
        return self.name


class ShippingMethodManager(models.Manager):
    """Model manager for ShippingMethod."""

    def get_shipping_price(self, country, channel, product_type, weight, price):
        """Return the lowest available matching shipping price."""
        shipping_methods = self.match_shipping_methods(
            country=country,
            product_type=product_type,
            channel=channel,
            weight=weight,
            price=price,
        )
        if len(shipping_methods) == 0:
            raise NoShippingService(
                (
                    f'No shipping method found for "{product_type}" to "{country}"" '
                    f"at {weight}g and {price}p"
                )
            )
        shipping_prices = self._get_prices_for_shipping_methods(
            shipping_methods=shipping_methods, weight=weight
        )
        try:
            return shipping_prices[0]
        except IndexError:
            raise NoShippingService(
                (
                    f'No shipping price found for "{product_type}" to "{country}"" '
                    f"at {weight}g and {price}p"
                )
            )

    def _get_prices_for_shipping_methods(self, shipping_methods, weight):
        prices = []
        for method in shipping_methods:
            try:
                price = method.shipping_price(weight)
            except NoShippingService:
                pass
            else:
                prices.append((method, price))
        prices.sort(key=lambda x: x[1])
        return prices

    def match_shipping_methods(self, country, product_type, weight, price, channel):
        """Return shipping methods for a given country, product type, weight and price."""
        return self.filter(
            country=country,
            product_type=product_type,
            channel=channel,
            min_weight__lte=weight,
            min_price__lte=price,
            inactive=False,
        ).filter(
            Q(
                Q(Q(max_price__isnull=True) | Q(max_price__gte=price))
                & Q(Q(max_weight__isnull=True) | Q(max_weight__gte=weight))
            )
        )


class ShippingMethod(models.Model):
    """Model for shipping methods."""

    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    shipping_service = models.ForeignKey(ShippingService, on_delete=models.PROTECT)
    product_type = models.ManyToManyField(ProductType)
    channel = models.ManyToManyField(Channel, blank=True)
    min_weight = models.PositiveIntegerField(default=0)
    max_weight = models.PositiveIntegerField(null=True, blank=True)
    min_price = models.PositiveIntegerField(default=0)
    max_price = models.PositiveIntegerField(null=True, blank=True)
    vat_rates = models.ManyToManyField(VATRate, blank=True)
    inactive = models.BooleanField(default=False)

    objects = ShippingMethodManager()

    class Meta:
        """Meta class for ShippingMethod."""

        verbose_name = "Shipping Method"
        verbose_name_plural = "Shippng Method"

    def __str__(self):
        return self.name

    def product_type_string(self):
        """Return package type as a string."""
        return ", ".join([x.name for x in self.product_type.all()])

    def shipping_price(self, weight):
        """Return the price for shipping a given weight by this method."""
        shipping_price = self._get_shipping_price()
        return shipping_price.price(weight)

    def _get_shipping_price(self):
        try:
            shipping_price = ShippingPrice.objects.get(
                country=self.country,
                shipping_service=self.shipping_service,
                inactive=False,
            )
        except ShippingPrice.DoesNotExist:
            raise NoShippingService(
                (
                    f'No price found for country "{self.country.name}" and '
                    f'service "{self.shipping_service.name}"'
                )
            )
        else:
            return shipping_price


class NoShippingService(Exception):
    """Exception for failed attempts to find a valid shipping service."""

    def __init__(self, *args, **kwargs):
        """Raise exception."""
        super().__init__(self, "No shipping service found.", *args, **kwargs)
