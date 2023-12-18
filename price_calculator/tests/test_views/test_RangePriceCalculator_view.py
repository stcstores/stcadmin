import pytest
from pytest_django.asserts import assertTemplateUsed


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def range_id(product_range):
    return product_range.pk


@pytest.fixture
def url(range_id):
    return f"/price_calculator/price_calculator/{range_id}/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def countries(country_factory):
    return [country_factory.create() for _ in range(3)]


@pytest.fixture
def channel_fees(channel_fee_factory):
    return [channel_fee_factory.create() for _ in range(3)]


@pytest.fixture
def channels(channel_factory):
    return [channel_factory.create() for _ in range(3)]


@pytest.mark.django_db
def test_logged_out_get_method(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_get(valid_get_response):
    assert valid_get_response.status_code == 200


@pytest.mark.django_db
def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


@pytest.mark.django_db
def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(
            valid_get_response, "price_calculator/range_price_calculator.html"
        )
        is not False
    )


@pytest.mark.django_db
def test_range_in_context(product_range, valid_get_response):
    assert valid_get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_countries_in_context(
    shipping_method_factory, countries, valid_get_request, url
):
    shipping_method_factory.create(country=countries[1])
    shipping_method_factory.create(country=countries[2])
    response = valid_get_request(url)
    assert list(response.context["countries"]) == [countries[1], countries[2]]


@pytest.mark.django_db
def test_channel_fees_in_context(channel_fees, valid_get_response):
    assert list(valid_get_response.context["channel_fees"]) == channel_fees


@pytest.mark.django_db
def test_channels_in_context(channels, valid_get_response):
    assert list(valid_get_response.context["channels"]) == channels
