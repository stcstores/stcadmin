import pytest
from pytest_django.asserts import assertTemplateUsed


@pytest.fixture
def url():
    return "/price_calculator/price_calculator/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def countries(country_factory):
    return [country_factory.create() for _ in range(3)]


@pytest.fixture
def product_types(product_type_factory):
    return [product_type_factory.create() for _ in range(3)]


@pytest.fixture
def channel_fees(channel_fee_factory):
    return [channel_fee_factory.create() for _ in range(3)]


@pytest.fixture
def channels(channel_factory):
    return [channel_factory.create() for _ in range(3)]


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
    assert "Price Calculator</h3>" in valid_get_response_content


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "price_calculator/price_calculator.html")
        is not False
    )


@pytest.mark.django_db
def test_countries_in_context(
    countries, shipping_method_factory, valid_get_request, url
):
    shipping_method_factory.create(country=countries[1])
    shipping_method_factory.create(country=countries[2])
    response = valid_get_request(url)
    assert list(response.context["countries"]) == [countries[1], countries[2]]


@pytest.mark.django_db
def test_product_types_in_context(product_types, valid_get_response):
    assert list(valid_get_response.context["product_types"]) == product_types


@pytest.mark.django_db
def test_channel_fees_in_context(channel_fees, valid_get_response):
    assert list(valid_get_response.context["channel_fees"]) == channel_fees


@pytest.mark.django_db
def test_channels_in_context(channels, valid_get_response):
    assert list(valid_get_response.context["channels"]) == channels
