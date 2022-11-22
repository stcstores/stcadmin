"""Model factories for the inventory app."""

import datetime as dt
import string

import factory
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.timezone import make_aware
from factory import fuzzy
from factory.django import DjangoModelFactory

from inventory import models


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"Test User {n}")
    password = hash("Password")


class BarcodeFactory(DjangoModelFactory):
    class Meta:

        model = models.Barcode

    class Params:
        used = False

    barcode = fuzzy.FuzzyText(length=12, chars=string.digits)
    available = factory.lazy_attribute(lambda o: False if o.used is True else True)
    added_on = factory.Maybe(
        "used", fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1))), None
    )
    used_by = factory.Maybe("used", factory.SubFactory(UserFactory), None)
    used_for = factory.Maybe("used", fuzzy.FuzzyText(length=25), None)


class PackageTypeFactory(DjangoModelFactory):
    class Meta:
        model = models.PackageType

    name = factory.Sequence(lambda n: f"Package Type {n}")
    large_letter_compatible = False
    ordering = 0
    active = True


class BrandFactory(DjangoModelFactory):
    class Meta:
        model = models.Brand

    name = factory.Sequence(lambda n: f"Brand {n}")
    active = True


class ManufacturerFactory(DjangoModelFactory):
    class Meta:
        model = models.Manufacturer

    name = factory.Sequence(lambda n: f"Brand {n}")
    active = True


class VATRateFactory(DjangoModelFactory):
    class Meta:
        model = models.VATRate

    name = factory.Sequence(lambda n: f"VAT Rate {n}")
    percentage = 0.2
    ordering = 0


class SupplierFactory(DjangoModelFactory):
    class Meta:
        model = models.Supplier

    name = factory.Sequence(lambda n: f"Supplier {n}")
    active = True


class SupplierContactFactory(DjangoModelFactory):
    class Meta:
        model = models.SupplierContact

    supplier = factory.SubFactory(SupplierFactory)
    name = "John Doe"
    email = "noone@nowhere.com"
    phone = "12345679"
    notes = "Call on Fridays"
    created_at = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))
    modified_at = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))


class ProductRangeFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductRange

    status = models.ProductRange.COMPLETE
    sku = factory.Sequence(lambda n: f"RNG_AAA-BBB-{n:03.0f}")
    name = factory.Sequence(lambda n: f"Product Range {n}")
    description = "Description Text"
    search_terms = [f"Term {i}" for i in range(5)]
    bullet_points = [f"Bullet {i}" for i in range(5)]
    is_end_of_line = False
    hidden = False
    managed_by = factory.SubFactory(UserFactory)
    created_at = make_aware(dt.datetime(2022, 3, 25, 13, 45, 54, 775))


class BaseProductFactory(DjangoModelFactory):
    class Meta:
        model = models.BaseProduct

    product_range = factory.SubFactory(ProductRangeFactory)
    sku = factory.Sequence(lambda n: f"AAA-BBB-00{n}")
    retail_price = None
    supplier = factory.SubFactory(SupplierFactory)
    barcode = "951467812546"
    supplier_barcode = ""
    package_type = factory.SubFactory(PackageTypeFactory)
    width = 500
    height = 500
    depth = 500
    is_end_of_line = False
    range_order = 0


class ProductFactory(BaseProductFactory):
    class Meta:
        model = models.Product

    purchase_price = 5.00
    brand = factory.SubFactory(BrandFactory)
    manufacturer = factory.SubFactory(ManufacturerFactory)
    weight_grams = 500
    hs_code = "2315641"
    vat_rate = factory.SubFactory(VATRateFactory)


class InitialVariationFactory(ProductFactory):
    class Meta:
        model = models.InitialVariation


class MultipackProductFactory(BaseProductFactory):
    class Meta:
        model = models.MultipackProduct

    base_product = factory.SubFactory(ProductFactory)
    quantity = 3
    name = "Pack of 3"


class CombinationProductFactory(BaseProductFactory):
    class Meta:
        model = models.CombinationProduct


class CombinationProductLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.CombinationProductLink

    product = factory.SubFactory(ProductFactory)
    combination_product = factory.SubFactory(CombinationProductFactory)
    quantity = 5


class StockLevelHistoryFactory(DjangoModelFactory):
    class Meta:
        model = models.StockLevelHistory

    class Params:
        initial = False

    source = models.StockLevelHistory.USER
    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(BaseProductFactory)
    stock_level = 5
    previous_change = factory.SubFactory(
        "inventory.factories.StockLevelHistoryFactory",
        previous_change=None,
    )


class BayFactory(DjangoModelFactory):
    class Meta:
        model = models.Bay

    name = factory.Sequence(lambda n: f"A-00{n}")
    active = True


class ProductBayLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductBayLink

    product = factory.SubFactory(ProductFactory)
    bay = factory.SubFactory(BayFactory)


class ProductBayHistoryFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductBayHistory

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    bay = factory.SubFactory(BayFactory)
    change = models.ProductBayHistory.ADDED


class VariationOptionFactory(DjangoModelFactory):
    class Meta:
        model = models.VariationOption

    name = factory.Sequence(lambda n: f"Variation Option {n}")
    ordering = 0
    active = True


class ListingAttributeFactory(DjangoModelFactory):
    class Meta:
        model = models.ListingAttribute

    name = factory.Sequence(lambda n: f"Listing Attribute {n}")
    ordering = 0
    active = True


class VariationOptionValueFactory(DjangoModelFactory):
    class Meta:
        model = models.VariationOptionValue

    product = factory.SubFactory(ProductFactory)
    variation_option = factory.SubFactory(VariationOptionFactory)
    value = factory.Sequence(lambda n: f"Variation Value {n}")


class ListingAttributeValueFactory(DjangoModelFactory):
    class Meta:
        model = models.ListingAttributeValue

    product = factory.SubFactory(ProductFactory)
    listing_attribute = factory.SubFactory(ListingAttributeFactory)
    value = factory.Sequence(lambda n: f"Listing Attribute {n}")


class ProductImageFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductImage

    image_file = factory.LazyAttribute(
        lambda _: ContentFile(
            factory.django.ImageField()._make_data({"width": 2000, "height": 2000}),
            "example.jpg",
        )
    )
    hash = fuzzy.FuzzyText(length=32, chars=string.digits)
    created_at = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))
    modified_at = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))


class ProductImageLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductImageLink

    product = factory.SubFactory(BaseProductFactory)
    image = factory.SubFactory(ProductImageFactory)
    created_at = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))
    modified_at = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))
    position = fuzzy.FuzzyInteger(0)


class ProductRangeImageLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductRangeImageLink

    product_range = factory.SubFactory(ProductRangeFactory)
    image = factory.SubFactory(ProductImageFactory)
    created_at = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))
    modified_at = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))
    position = fuzzy.FuzzyInteger(0, 50)
