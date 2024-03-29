"""Model factories for the inventory app."""

import datetime as dt
from decimal import Decimal

import factory
from django.core.files.base import ContentFile
from factory.django import DjangoModelFactory

from home.factories import UserFactory
from inventory import models


class BarcodeFactory(DjangoModelFactory):
    class Meta:
        model = models.Barcode

    class Params:
        used = False

    barcode = factory.Faker("ean")
    available = factory.lazy_attribute(lambda o: False if o.used is True else True)
    added_on = factory.Maybe(
        "used",
        factory.Faker("date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc),
        None,
    )
    used_by = factory.Maybe("used", factory.SubFactory(UserFactory), None)
    used_for = factory.Maybe("used", factory.Faker("text", max_nb_chars=50), None)


class PackageTypeFactory(DjangoModelFactory):
    class Meta:
        model = models.PackageType

    name = factory.Faker("text", max_nb_chars=50)
    large_letter_compatible = False
    ordering = 0
    active = True


class BrandFactory(DjangoModelFactory):
    class Meta:
        model = models.Brand

    name = factory.Faker("text", max_nb_chars=50)
    active = True


class ManufacturerFactory(DjangoModelFactory):
    class Meta:
        model = models.Manufacturer

    name = factory.Faker("text", max_nb_chars=50)
    active = True


class VATRateFactory(DjangoModelFactory):
    class Meta:
        model = models.VATRate

    name = factory.Faker("text", max_nb_chars=50)
    percentage = 0.2
    ordering = 0


class SupplierFactory(DjangoModelFactory):
    class Meta:
        model = models.Supplier

    name = factory.Faker("text", max_nb_chars=50)
    active = True
    blacklisted = False
    last_ordered_from = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    restock_comment = factory.Faker("paragraph")


class SupplierContactFactory(DjangoModelFactory):
    class Meta:
        model = models.SupplierContact

    supplier = factory.SubFactory(SupplierFactory)
    name = factory.Faker("name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    notes = factory.Faker("text", max_nb_chars=50)
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class ProductRangeFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductRange

    status = models.ProductRange.COMPLETE
    sku = factory.Faker("lexify", text="RNG_???-???-???")
    name = factory.Faker("text", max_nb_chars=50)
    description = factory.Faker("paragraph")
    search_terms = [f"Term {i}" for i in range(5)]
    bullet_points = [f"Bullet {i}" for i in range(5)]
    managed_by = factory.SubFactory(UserFactory)
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class BaseProductFactory(DjangoModelFactory):
    class Meta:
        model = models.BaseProduct

    product_range = factory.SubFactory(ProductRangeFactory)
    sku = factory.Faker("lexify", text="???-???-???")
    retail_price = factory.Faker(
        "pydecimal", right_digits=2, positive=True, max_value=200
    )
    supplier = factory.SubFactory(SupplierFactory)
    barcode = factory.Faker("ean")
    supplier_barcode = factory.Faker("ean")
    supplier_sku = factory.Faker("lexify", text="?" * 12)
    package_type = factory.SubFactory(PackageTypeFactory)
    width = factory.Faker("pyint", min_value=10, max_value=1000)
    height = factory.Faker("pyint", min_value=10, max_value=1000)
    depth = factory.Faker("pyint", min_value=10, max_value=1000)
    is_end_of_line = False
    is_archived = False
    range_order = 0
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class ProductFactory(BaseProductFactory):
    class Meta:
        model = models.Product

    purchase_price = Decimal("5.00")
    brand = factory.SubFactory(BrandFactory)
    manufacturer = factory.SubFactory(ManufacturerFactory)
    weight_grams = 500
    hs_code = "2315641"
    vat_rate = factory.SubFactory(VATRateFactory)
    is_flammable = False


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

    source = factory.Faker(
        "random_element",
        elements=(
            models.StockLevelHistory.USER,
            models.StockLevelHistory.IMPORT,
            models.StockLevelHistory.API,
        ),
    )
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

    name = factory.Faker("text", max_nb_chars=50)
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
    change = factory.Faker(
        "random_element",
        elements=(models.ProductBayHistory.ADDED, models.ProductBayHistory.REMOVED),
    )


class VariationOptionFactory(DjangoModelFactory):
    class Meta:
        model = models.VariationOption

    name = factory.Faker("text", max_nb_chars=50)
    ordering = 0
    active = True


class ListingAttributeFactory(DjangoModelFactory):
    class Meta:
        model = models.ListingAttribute

    name = factory.Faker("text", max_nb_chars=50)
    ordering = 0
    active = True


class VariationOptionValueFactory(DjangoModelFactory):
    class Meta:
        model = models.VariationOptionValue

    product = factory.SubFactory(ProductFactory)
    variation_option = factory.SubFactory(VariationOptionFactory)
    value = factory.Faker("text", max_nb_chars=50)


class ListingAttributeValueFactory(DjangoModelFactory):
    class Meta:
        model = models.ListingAttributeValue

    product = factory.SubFactory(ProductFactory)
    listing_attribute = factory.SubFactory(ListingAttributeFactory)
    value = factory.Faker("text", max_nb_chars=50)


class ProductImageFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductImage

    image_file = factory.LazyAttribute(
        lambda _: ContentFile(
            factory.django.ImageField()._make_data({"width": 2000, "height": 2000}),
            "example.jpg",
        )
    )
    hash = factory.Faker("numerify", text="#" * 32)
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class ProductImageLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductImageLink

    product = factory.SubFactory(BaseProductFactory)
    image = factory.SubFactory(ProductImageFactory)
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    position = factory.Faker("pyint", min_value=0, max_value=50)


class ProductRangeImageLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductRangeImageLink

    product_range = factory.SubFactory(ProductRangeFactory)
    image = factory.SubFactory(ProductImageFactory)
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    position = factory.Faker("pyint", min_value=0, max_value=50)
