"""Models for price_calculator app."""

from django.db import models
from django.db.models import Q

from shipping.models import Country


class DestinationCountry(models.Model):
    """Model for countries to ship to."""

    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, null=True, blank=True
    )
    min_channel_fee = models.IntegerField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        """Meta class for DestinationCountry."""

        verbose_name = "Destination Country"
        verbose_name_plural = "Destination Countries"
        ordering = ("sort_order",)

    class NoShippingService(Exception):
        """Exception for failed attempts to find a valid shipping service."""

        def __init__(self, *args, **kwargs):
            """Raise exception."""
            super().__init__(self, "No shipping service found.", *args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def currency_code(self):
        """Return the countries currency code."""
        return self.country.currency.code

    @property
    def currency_symbol(self):
        """Return the countries currency symbol."""
        return self.country.currency.symbol

    @property
    def exchange_rate(self):
        """Return the countries currency exhange rate to GBP."""
        return self.country.currency.exchange_rate


class PackageType(models.Model):
    """Model for types of packaging."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        """Meta class for PackageType."""

        verbose_name = "Package Type"
        verbose_name_plural = "Package Types"

    def __str__(self):
        return self.name


class VATRate(models.Model):
    """Model for VAT rates."""

    name = models.CharField(max_length=50)
    cc_id = models.PositiveSmallIntegerField()
    percentage = models.PositiveSmallIntegerField()

    class Meta:
        """Meta class for VATRate."""

        verbose_name = "VAT Rate"
        verbose_name_plural = "VAT Rates"

    def __str__(self):
        return self.name


class ShippingPrice(models.Model):
    """Model for shipping prices."""

    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(DestinationCountry, on_delete=models.CASCADE)
    package_type = models.ManyToManyField(PackageType)
    min_weight = models.PositiveSmallIntegerField(null=True, blank=True)
    max_weight = models.PositiveSmallIntegerField(null=True, blank=True)
    min_price = models.PositiveSmallIntegerField(null=True, blank=True)
    max_price = models.PositiveSmallIntegerField(null=True, blank=True)
    item_price = models.PositiveSmallIntegerField()
    kilo_price = models.PositiveSmallIntegerField(null=True, blank=True)
    vat_rates = models.ManyToManyField(VATRate, blank=True)
    disabled = models.BooleanField(default=False)

    class Meta:
        """Meta class for ShippingPrice."""

        verbose_name = "Shipping Price"
        verbose_name_plural = "Shippng Prices"

    def __str__(self):
        return self.name

    def calculate(self, weight):
        """Return the final price for a given weight."""
        return self.item_price + self.calculate_kilos(weight)

    def calculate_kilos(self, weight):
        """Calculate price for weight."""
        if self.kilo_price is None:
            return 0
        return int((self.kilo_price / 1000) * weight)

    def package_type_string(self):
        """Return package type as a string."""
        return ", ".join([x.name for x in self.package_type.all()])

    @classmethod
    def get_price(cls, country_name, package_type_name, weight, price):
        """Return best match price object."""
        country = DestinationCountry.objects.get(name__icontains=country_name)
        package_type = PackageType.objects.get(name__icontains=package_type_name)
        shipping_prices = cls._default_manager.filter(Q(country=country))
        shipping_prices = shipping_prices.filter(Q(disabled=False))
        shipping_prices = shipping_prices.filter(Q(package_type=package_type))
        shipping_prices = shipping_prices.filter(
            Q(min_weight__isnull=True) | Q(min_weight__lte=weight)
        )
        shipping_prices = shipping_prices.filter(
            Q(max_weight__isnull=True) | Q(max_weight__gte=weight)
        )
        shipping_prices = shipping_prices.filter(
            Q(min_price__isnull=True) | Q(min_price__lte=price)
        )
        shipping_prices = shipping_prices.filter(
            Q(max_price__isnull=True) | Q(max_price__gte=price)
        )
        try:
            return cls._default_manager.get(pk=shipping_prices.all()[0].id)
        except IndexError:
            raise DestinationCountry.NoShippingService()


class ChannelFee(models.Model):
    """Model for channel fees."""

    name = models.CharField(max_length=50, unique=True)
    fee_percentage = models.PositiveSmallIntegerField()
    ordering = models.PositiveSmallIntegerField(default=100)

    class Meta:
        """Meta class for ChannelFee."""

        verbose_name = "Channel Fee"
        verbose_name_plural = "Channel Fees"
        ordering = ("ordering",)

    def __str__(self):
        return self.name
