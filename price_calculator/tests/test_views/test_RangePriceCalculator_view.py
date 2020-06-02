from unittest.mock import patch

import pytest
from pytest_django.asserts import assertTemplateUsed

from inventory.tests import mocks


@pytest.fixture
def range_id():
    return "9186461"


@pytest.fixture
def url(range_id):
    return f"/price_calculator/price_calculator/{range_id}/"


@pytest.fixture
def mock_range(range_id):
    mock_range = mocks.MockCCProductsProductRange(id=range_id)
    return mock_range


@pytest.fixture
def mock_cc_products(mock_range):
    with patch("price_calculator.views.cc_products") as mock_cc_products:
        mock_cc_products.get_range.return_value = mock_range
        yield mock_cc_products


@pytest.fixture
def valid_get_response(mock_cc_products, valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def countries(country_factory):
    return [country_factory.create() for _ in range(3)]


@pytest.fixture
def channel_fees(channel_fee_factory):
    return [channel_fee_factory.create() for _ in range(3)]


def test_logged_out_get_method(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(valid_get_response):
    assert valid_get_response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


def test_heading(valid_get_response_content):
    assert "Price Calculator</h1>" in valid_get_response_content


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(
            valid_get_response, "price_calculator/range_price_calculator.html"
        )
        is not False
    )


def test_requests_range(range_id, mock_cc_products, valid_get_response):
    assert mock_cc_products.get_range.called_once_with(range_id)


def test_range_in_context(mock_range, valid_get_response):
    assert valid_get_response.context["product_range"] == mock_range


@pytest.mark.django_db
def test_countries_in_context(
    mock_cc_products, shipping_method_factory, countries, valid_get_request, url
):
    shipping_method_factory.create(country=countries[1])
    shipping_method_factory.create(country=countries[2])
    response = valid_get_request(url)
    assert list(response.context["countries"]) == [countries[1], countries[2]]


@pytest.mark.django_db
def test_channel_fees_in_context(channel_fees, valid_get_response):
    assert list(valid_get_response.context["channel_fees"]) == channel_fees
