"""Model factories for the Channels app."""

import datetime as dt

import factory
from factory.django import DjangoModelFactory

from channels import models
from inventory.factories import ProductFactory, ProductRangeFactory


class ShopifyConfigFactory(DjangoModelFactory):
    class Meta:
        model = models.shopify_models.ShopifyConfig

    location_id = "AAAAAABBB111"


class ShopifyTagFactory(DjangoModelFactory):
    class Meta:
        model = models.shopify_models.ShopifyTag

    name = factory.Faker("pystr", min_chars=14, max_chars=14)


class ShopifyCollectionFactory(DjangoModelFactory):
    class Meta:
        model = models.shopify_models.ShopifyCollection

    name = factory.Faker("pystr", min_chars=14, max_chars=14)
    collection_id = factory.Faker("pyint", max_value=9999999, min_value=999999)


class ShopifyListingFactory(DjangoModelFactory):
    class Meta:
        model = models.shopify_models.ShopifyListing

    product_range = factory.SubFactory(ProductRangeFactory)
    title = factory.Faker("pystr", min_chars=14, max_chars=36)
    product_id = factory.Faker("pyint", max_value=9999999, min_value=999999)


class ShopifyVariationFactory(DjangoModelFactory):
    class Meta:
        model = models.shopify_models.ShopifyVariation

    listing = factory.SubFactory(ShopifyListingFactory)
    product = factory.SubFactory(ProductFactory)
    price = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    variant_id = factory.Faker("pyint", max_value=9999999, min_value=999999)
    inventory_item_id = factory.Faker("pyint", max_value=9999999, min_value=999999)


class ShopifyUpdateFactory(DjangoModelFactory):
    class Meta:
        model = models.shopify_models.ShopifyUpdate

    listing = factory.SubFactory(ShopifyListingFactory)
    operation_type = models.shopify_models.ShopifyUpdate.UPDATE_PRODUCT
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    completed_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    error = False
