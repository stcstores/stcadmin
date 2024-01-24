from unittest import mock

import pytest
from django.urls import reverse

from channels.models.shopify_models import ShopifyListing, ShopifyUpdate
from channels.views import ShopifyListingStatus


@pytest.fixture
def template():
    return "channels/shopify/shopify_listing_status.html"


def test_template_name_attribute(template):
    assert ShopifyListingStatus.template_name == template


@pytest.fixture
def listing_pk():
    return 99


@pytest.fixture
def url(listing_pk):
    return reverse("channels:shopify_listing_status", args=[listing_pk])


@pytest.fixture
def mock_get_object():
    with mock.patch("channels.views.get_object_or_404") as m:
        yield m


@pytest.fixture
def get_response(mock_get_object, group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response, template):
    assert template in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_calls_get_object_or_404(mock_get_object, get_response, listing_pk):
    mock_get_object.assert_called_once_with(ShopifyListing, pk=listing_pk)


def test_calls_get_last_update(mock_get_object, get_response):
    mock_get_object.return_value.get_last_update.assert_called_once_with()
    assert (
        get_response.context["update"]
        == mock_get_object.return_value.get_last_update.return_value
    )


def test_get_last_update_error(mock_get_object, group_logged_in_client, url):
    mock_get_object.return_value.get_last_update.return_value.completed_at = None
    mock_get_object.return_value.get_last_update.side_effect = (
        ShopifyUpdate.DoesNotExist
    )
    response = group_logged_in_client.get(url)
    assert response.context["ongoing"] is False


def test_ongoing_with_completed_update(mock_get_object, group_logged_in_client, url):
    mock_get_object.return_value.get_last_update.return_value.completed_at = True
    response = group_logged_in_client.get(url)
    assert response.context["ongoing"] is False


def test_ongoing_with_incomplete_update(mock_get_object, group_logged_in_client, url):
    mock_get_object.return_value.get_last_update.return_value.completed_at = None
    response = group_logged_in_client.get(url)
    assert response.context["ongoing"] is True


def test_listing_without_id(mock_get_object, group_logged_in_client, url):
    mock_get_object.return_value.product_id = None
    response = group_logged_in_client.get(url)
    assert response.context["uploaded"] is False
    assert response.context["active"] is False


def test_listing_with_id(mock_get_object, group_logged_in_client, url):
    mock_get_object.return_value.product_id = 1
    response = group_logged_in_client.get(url)
    mock_get_object.return_value.listing_is_active.assert_called_once_with()
    assert response.context["uploaded"] is True
    assert (
        response.context["active"]
        == mock_get_object.return_value.listing_is_active.return_value
    )
