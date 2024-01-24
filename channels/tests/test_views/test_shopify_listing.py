from unittest import mock

import pytest
from django.urls import reverse

from channels import models
from channels.views import ShopifyListing


@pytest.fixture
def template():
    return "channels/shopify/shopify_listing.html"


def test_template_name_attribute(template):
    assert ShopifyListing.template_name == template


@pytest.fixture
def mock_get_object():
    with mock.patch("channels.views.get_object_or_404") as m:
        m.return_value.product_range.__getitem__.return_value = 4
        m.return_value.__getitem__.return_value = 8
        yield m


@pytest.fixture
def listing_pk():
    return 5


@pytest.fixture
def url(listing_pk):
    return reverse("channels:shopify_listing", args=[listing_pk])


@pytest.fixture
def get_response(mock_get_object, group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(template, get_response):
    assert template in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_calls_get_object_or_404(mock_get_object, listing_pk, get_response):
    mock_get_object.assert_called_once_with(
        models.shopify_models.ShopifyListing, pk=listing_pk
    )


def test_listing_in_context(mock_get_object, get_response):
    assert get_response.context["listing"] == mock_get_object.return_value


def test_product_range_in_context(mock_get_object, get_response):
    assert (
        get_response.context["product_range"]
        == mock_get_object.return_value.product_range
    )
