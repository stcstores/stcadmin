import json

import pytest


@pytest.fixture
def url():
    return "/price_calculator/get_shipping_price/"


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def weight():
    return 500


@pytest.fixture
def price():
    return 1500


@pytest.fixture
def international_shipping():
    return "Domestic"


@pytest.fixture
def product_type(product_type_factory):
    return product_type_factory.create()


@pytest.fixture
def channel(channel_factory):
    return channel_factory.create()


@pytest.fixture
def form_data(country, channel, weight, price, international_shipping, product_type):
    return {
        "country": country.name,
        "weight": weight,
        "price": price,
        "international_shipping": international_shipping,
        "package_type": product_type.name,
        "channel": channel.name,
    }


@pytest.fixture
def shipping_service(shipping_service_factory):
    return shipping_service_factory.create()


@pytest.fixture
def shipping_price(country, product_type, shipping_service, shipping_price_factory):
    return shipping_price_factory.create(
        country=country, shipping_service=shipping_service
    )


@pytest.fixture
def shipping_method(
    shipping_method_factory,
    vat_rate_factory,
    country,
    shipping_price,
    shipping_service,
    product_type,
    channel,
):
    shipping_method = shipping_method_factory.create(
        country=country, shipping_service=shipping_service
    )
    shipping_method.product_type.set([product_type])
    shipping_method.channel.set([channel])
    shipping_method.vat_rates.set([vat_rate_factory.create() for _ in range(2)])
    return shipping_method


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_post_response(valid_post_request, url, form_data):
    return valid_post_request(url, form_data)


@pytest.fixture
def valid_post_response_content(valid_post_response):
    return json.loads(valid_post_response.content.decode("utf8"))


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
def country_channel_fee(country, country_channel_fee_factory):
    min_channel_fee = 9
    country_channel_fee_factory.create(country=country, min_channel_fee=min_channel_fee)
    return min_channel_fee


def test_logged_out_get_method(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 405


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(valid_post_response):
    assert valid_post_response.status_code == 200


def test_response_without_valid_price(valid_post_response_content):
    assert valid_post_response_content == {
        "success": False,
        "price": 0,
        "price_name": "No Shipping Service Found",
        "vat_rates": [],
        "exchange_rate": 0,
        "currency_code": "GBP",
        "currency_symbol": "£",
        "min_channel_fee": 0,
    }


@pytest.mark.django_db
def test_response_with_valid_price(
    weight, shipping_method, valid_post_response_content
):
    assert valid_post_response_content == {
        "success": True,
        "price": shipping_method.shipping_price(weight),
        "price_name": shipping_method.name,
        "vat_rates": list(shipping_method.vat_rates.values()),
        "exchange_rate": shipping_method.country.currency.exchange_rate,
        "currency_code": shipping_method.country.currency.code,
        "currency_symbol": shipping_method.country.currency.symbol,
        "min_channel_fee": 0,
    }


@pytest.mark.django_db
def test_country_channel_fee(
    country, country_channel_fee, shipping_method, valid_post_response_content
):
    assert valid_post_response_content["min_channel_fee"] == int(
        country_channel_fee * country.currency.exchange_rate
    )
