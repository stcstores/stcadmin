import pytest

from channels.forms import ShopifyCollectionsForm


@pytest.fixture
def shopify_listing(shopify_listing_factory):
    return shopify_listing_factory.create()


@pytest.fixture
def collections(shopify_collection_factory):
    return shopify_collection_factory.create_batch(3)


@pytest.fixture
def form_data(collections):
    return {"collections": [collection for collection in collections]}


@pytest.mark.django_db
def test_form_submission(collections, shopify_listing, form_data):
    form = ShopifyCollectionsForm(form_data, instance=shopify_listing)
    assert form.is_valid() is True
    form.save()
    for collection in collections:
        assert form.instance.collections.all().contains(collection)


@pytest.mark.django_db
def test_remove_collections(collections, shopify_listing):
    shopify_listing.collections.set(collections)
    form = ShopifyCollectionsForm({"collections": []}, instance=shopify_listing)
    assert form.is_valid() is True
    form.save()
    assert shopify_listing.collections.count() == 0
