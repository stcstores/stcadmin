from unittest import mock

import pytest
from django.urls import reverse

from channels.models.shopify_models import ShopifyListing


@pytest.fixture
def mock_get_object():
    with mock.patch("channels.views.get_object_or_404") as m:
        yield m


@pytest.fixture
def form_data():
    return {"listing_pk": 99}


@pytest.fixture
def url():
    return reverse("channels:upload_shopify_listing")


@pytest.fixture
def post_response(url, group_logged_in_client, form_data):
    return group_logged_in_client.post(url, form_data)


def test_get_response(url, group_logged_in_client):
    response = group_logged_in_client.get(url)
    assert response.status_code == 405


def test_calls_get_object_or_404(mock_get_object, post_response, form_data):
    mock_get_object.assert_called_once_with(
        ShopifyListing, pk=str(form_data["listing_pk"])
    )


def test_calls_upload(mock_get_object, post_response):
    mock_get_object.return_value.upload.assert_called_once_with()


def test_response(mock_get_object, post_response):
    assert post_response.content.decode("utf8") == "ok"
