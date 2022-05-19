"""Model factories for the shipping app."""

from decimal import Decimal

import factory

from shipping import models


class CurrencyFactory(factory.django.DjangoModelFactory):
    """Factory for the shipping.Currency model."""

    class Meta:
        """Metaclass for shipping.factories.CurrencyFactory."""

        model = models.Currency

    name = factory.Sequence(lambda n: f"Test Currency {n}")
    code = factory.Sequence(lambda n: f"SD{n}")
    exchange_rate = Decimal(1.45)
    symbol = "$"


class RegionFactory(factory.django.DjangoModelFactory):
    """Factory for the shipping.Region model."""

    class Meta:
        """Metaclass for shipping.factories.RegionFactory."""

        model = models.Region

    name = factory.Sequence(lambda n: f"Test Currency {n}")
    abriviation = "EU"
    vat_required = "Variable"
    default_vat_rate = 20


class CountryFactory(factory.django.DjangoModelFactory):
    """Factory for the shipping.Country model."""

    class Meta:
        """Metaclass for shipping.factories.CountryFactory."""

        model = models.Country

    name = factory.Sequence(lambda n: f"Test Country {n}")
    ISO_code = "TC"
    region = factory.SubFactory(RegionFactory)
    currency = factory.SubFactory(CurrencyFactory)
    vat_required = "As Region"
    default_vat_rate = None


class ProviderFactory(factory.django.DjangoModelFactory):
    """Factory for the shipping.Provider model."""

    class Meta:
        """Metaclass for shipping.factories.ProviderFactory."""

        model = models.Provider

    name = factory.Sequence(lambda n: f"Test Provider {n}")
    active = True


class ShippingServiceFactory(factory.django.DjangoModelFactory):
    """Factory for the shipping.ShippingService model."""

    class Meta:
        """Metaclass for shipping.factories.ShippingServiceFactory."""

        model = models.ShippingService

    name = factory.Sequence(lambda n: f"Test Shipping Service {n}")
    priority = False
    active = True


class ShippingPriceFactory(factory.django.DjangoModelFactory):
    """Factory for the shipping.ShippingPriceFactory model."""

    class Meta:
        """Metaclass for shipping.factories.CurrencyFactory."""

        model = models.ShippingPrice

    shipping_service = factory.SubFactory(ShippingServiceFactory)
    country = factory.SubFactory(CountryFactory)
    region = None
    item_price = 550
    price_per_kg = 0
    item_surcharge = 0
    fuel_surcharge = 0
    covid_surcharge = 0
    active = True


class WeightBandFactory(factory.django.DjangoModelFactory):
    """Factory for the shipping.WeightBand model."""

    class Meta:
        """Metaclass for shipping.factories.WeightBandFactory."""

        model = models.WeightBand

    shipping_price = factory.SubFactory(ShippingPriceFactory)
    min_weight = 200
    max_weight = 500
    price = 720
