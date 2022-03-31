import datetime as dt

import factory
import pytest_factoryboy
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from inventory import models


@pytest_factoryboy.register
class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"Test User {n}")
    password = hash("Password")


@pytest_factoryboy.register
class BarcodeFactory(DjangoModelFactory):
    class Meta:
        model = models.Barcode

    barcode = factory.Sequence(lambda n: f"165456156{n}")
    available = True
    used_by = factory.SubFactory(UserFactory)


@pytest_factoryboy.register
class PackageTypeFactory(DjangoModelFactory):
    class Meta:
        model = models.PackageType

    name = factory.Sequence(lambda n: f"Package Type {n}")
    large_letter_compatible = False
    ordering = 0
    active = True


@pytest_factoryboy.register
class BrandFactory(DjangoModelFactory):
    class Meta:
        model = models.Brand

    name = factory.Sequence(lambda n: f"Brand {n}")
    active = True


@pytest_factoryboy.register
class ManufacturerFactory(DjangoModelFactory):
    class Meta:
        model = models.Manufacturer

    name = factory.Sequence(lambda n: f"Brand {n}")
    active = True


@pytest_factoryboy.register
class VATRateFactory(DjangoModelFactory):
    class Meta:
        model = models.VATRate

    name = factory.Sequence(lambda n: f"VAT Rate {n}")
    percentage = 20
    ordering = 0


@pytest_factoryboy.register
class SupplierFactory(DjangoModelFactory):
    class Meta:
        model = models.Supplier

    name = factory.Sequence(lambda n: f"Supplier {n}")
    active = True


@pytest_factoryboy.register
class ProductRangeFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductRange

    status = models.ProductRange.COMPLETE
    sku = factory.Sequence(lambda n: f"RNG_AAA-BBB-00{n}")
    name = factory.Sequence(lambda n: f"Product Range {n}")
    description = ""
    search_terms = list()
    bullet_points = list()
    is_end_of_line = False
    hidden = False
    managed_by = factory.SubFactory(UserFactory)
    created_at = dt.datetime(2022, 3, 25, 13, 45, 54, 775)


@pytest_factoryboy.register
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
    length_mm = 500
    height_mm = 500
    width_mm = 500
    is_end_of_line = False
    range_order = 0
    latest_stock_change = factory.post_generation(
        lambda obj, create, extracted, **kwargs: StockLevelHistoryFactory.create(
            product=obj
        )
    )


@pytest_factoryboy.register
class ProductFactory(BaseProductFactory):
    class Meta:
        model = models.Product

    purchase_price = 5.00
    brand = factory.SubFactory(BrandFactory)
    manufacturer = factory.SubFactory(ManufacturerFactory)
    weight_grams = 500
    hs_code = "2315641"


@pytest_factoryboy.register
class InitialVariationFactory(ProductFactory):
    class Meta:
        model = models.InitialVariation


@pytest_factoryboy.register
class MultipackProductFactory(BaseProductFactory):
    class Meta:
        model = models.MultipackProduct

    base_product = factory.SubFactory(ProductFactory)
    quantity = 3
    name = "Pack of 3"


@pytest_factoryboy.register
class CombinationProductFactory(BaseProductFactory):
    class Meta:
        model = models.CombinationProduct


@pytest_factoryboy.register
class CombinationProductLink(DjangoModelFactory):
    class Meta:
        model = models.CombinationProductLink

    product = factory.SubFactory(ProductFactory)
    combination_product = factory.SubFactory(CombinationProductFactory)
    quantity = 5


@pytest_factoryboy.register
class StockLevelHistoryFactory(DjangoModelFactory):
    class Meta:
        model = models.StockLevelHistory

    source = models.StockLevelHistory.USER
    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    stock_level = 5
    previous_change = None


@pytest_factoryboy.register
class BayFactory(DjangoModelFactory):
    class Meta:
        model = models.Bay

    name = factory.Sequence(lambda n: f"A-00{n}")
    active = True


@pytest_factoryboy.register
class ProductBayLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductBayLink

    product = factory.SubFactory(ProductFactory)
    bay = factory.SubFactory(BarcodeFactory)


@pytest_factoryboy.register
class ProductBayHistoryFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductBayHistory

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    bay = factory.SubFactory(BayFactory)
    change = models.ProductBayHistory.ADDED


@pytest_factoryboy.register
class VariationOptionFactory(DjangoModelFactory):
    class Meta:
        model = models.VariationOption

    name = factory.Sequence(lambda n: f"Variation Option {n}")
    ordering = 0
    active = True


@pytest_factoryboy.register
class ListingAttributeFactory(DjangoModelFactory):
    class Meta:
        model = models.ListingAttribute

    name = factory.Sequence(lambda n: f"Listing Attribute {n}")
    ordering = 0
    active = True


@pytest_factoryboy.register
class VariationOptionValueFactory(DjangoModelFactory):
    class Meta:
        model = models.VariationOptionValue

    product = factory.SubFactory(ProductFactory)
    variation_option = factory.SubFactory(VariationOptionFactory)
    value = factory.Sequence(lambda n: f"Variation Value {n}")


@pytest_factoryboy.register
class ListingAttributeValueFactory(DjangoModelFactory):
    class Meta:
        model = models.ListingAttributeValue

    product = factory.SubFactory(ProductFactory)
    variation_option = factory.SubFactory(VariationOptionFactory)
    value = factory.Sequence(lambda n: f"Variation Value {n}")
