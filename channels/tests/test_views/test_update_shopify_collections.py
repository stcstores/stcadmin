from unittest import mock

import pytest
from django.urls import reverse

from channels.forms import ShopifyCollectionsForm
from channels.models.shopify_models import ShopifyListing
from channels.views import UpdateShopifyCollections


@pytest.fixture
def template():
    return "channels/shopify/shopify_collections_form.html"


def test_template_name_attribute(template):
    assert UpdateShopifyCollections.template_name == template


def test_form_class_attribute():
    assert UpdateShopifyCollections.form_class == ShopifyCollectionsForm


def test_model_attribute():
    assert UpdateShopifyCollections.model == ShopifyListing


@pytest.fixture
def collection(shopify_collection_factory):
    return shopify_collection_factory.create()


@pytest.fixture
def shopify_listing(shopify_listing_factory, collection):
    shopify_listing = shopify_listing_factory.create()
    shopify_listing.collections.set([collection])
    return shopify_listing


@pytest.fixture
def collections(shopify_collection_factory):
    return shopify_collection_factory.create_batch(3)


@pytest.fixture
def mock_shopify_collection():
    with mock.patch("channels.views.models.shopify_models.ShopifyCollection") as m:
        yield m


@pytest.fixture
def url(mock_shopify_collection, shopify_listing):
    return reverse("channels:update_shopify_collections", args=[shopify_listing.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(template, get_response):
    assert template in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], ShopifyCollectionsForm)


@pytest.mark.django_db
def test_listing_in_context(shopify_listing, get_response):
    assert get_response.context["listing"] == shopify_listing


@pytest.mark.django_db
def test_listing_collections_in_context(collection, get_response):
    value = get_response.context["listing_collections"]
    assert list(value) == [collection]


def test_all_collections_in_context(mock_shopify_collection, get_response):
    mock_shopify_collection.objects.all.assert_called_once_with()
    value = get_response.context["all_collections"]
    assert value == mock_shopify_collection.objects.all.return_value


@pytest.fixture
def form_data(collections):
    return {"collections": [collection.id for collection in collections]}


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_redirect(post_response, shopify_listing):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse(
        "channels:update_shopify_tags", kwargs={"pk": shopify_listing.pk}
    )


@pytest.mark.django_db
def test_sets_tags(collections, shopify_listing, post_response):
    for collection in collections:
        assert shopify_listing.collections.all().contains(collection)
