"""Models for price_calculator app."""

from django.db import models
from django.db.models import Q
from forex_python.converter import CurrencyRates


class DestinationCountry(models.Model):
    """Model for countries to ship to."""

    name = models.CharField(max_length=50, unique=True)
    currency_code = models.CharField(max_length=4, default='GBP')
    min_channel_fee = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    def current_rate(self):
        """Return current currency conversion rate to GBP."""
        if self.currency_code == 'GBP':
            return 1
        c = CurrencyRates()
        return c.get_rate(str(self.currency_code), 'GBP')


class PackageType(models.Model):
    """Model for types of packaging."""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class VATRate(models.Model):
    """Model for VAT rates."""

    name = models.CharField(max_length=50)
    cc_id = models.PositiveSmallIntegerField()
    percentage = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class ShippingPriceManager(models.Manager):
    """Model manager for shipping prices."""

    def get_price_for_product(self, country_name, price, product):
        """Return guideline price for product."""
        package_type_name = str(product.options['Package Type'].value)
        weight = product.weight
        return self.get_price(country_name, package_type_name, weight)

    def get_price(self, country_name, package_type_name, weight, price):
        """Return best match price object."""
        country = DestinationCountry.objects.get(name__icontains=country_name)
        package_type = PackageType.objects.get(
            name__icontains=package_type_name)
        shipping_prices = self.get_queryset().filter(Q(country=country))
        shipping_prices = shipping_prices.filter(Q(package_type=package_type))
        shipping_prices = shipping_prices.filter(
            Q(min_weight__isnull=True) | Q(min_weight__lte=weight))
        shipping_prices = shipping_prices.filter(
            Q(max_weight__isnull=True) | Q(max_weight__gte=weight))
        shipping_prices = shipping_prices.filter(
            Q(min_price__isnull=True) | Q(min_price__lte=price))
        shipping_prices = shipping_prices.filter(
            Q(max_price__isnull=True) | Q(max_price__gte=price))
        return self.get(pk=shipping_prices.all()[0].id)

    def get_calculated_price(
            self, country_name, package_type_name, weight, price):
        """Return price after weight caluclation."""
        return self.get_price(
            country_name, package_type_name, weight, price).calculate(weight)

    def calculate_price_for_product(self, country_name, price, product):
        """Return cost of sending a product to a country."""
        return self.get_price_for_product(
            country_name, price, product).calculate()


class ShippingPrice(models.Model):
    """Model for shipping prices."""

    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(
        DestinationCountry, on_delete=models.CASCADE)
    package_type = models.ManyToManyField(PackageType)
    min_weight = models.PositiveSmallIntegerField(null=True, blank=True)
    max_weight = models.PositiveSmallIntegerField(null=True, blank=True)
    min_price = models.PositiveSmallIntegerField(null=True, blank=True)
    max_price = models.PositiveSmallIntegerField(null=True, blank=True)
    item_price = models.PositiveSmallIntegerField()
    kilo_price = models.PositiveSmallIntegerField(null=True, blank=True)
    vat_rates = models.ManyToManyField(VATRate, blank=True)

    objects = ShippingPriceManager()

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
        return ', '.join([x.name for x in self.package_type.all()])
