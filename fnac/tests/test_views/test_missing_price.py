import pytest
from django.shortcuts import reverse


@pytest.fixture
def url():
    return "/fnac/missing_price/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_post_response(valid_post_request, url, post_data):
    return valid_post_request(url, post_data)


@pytest.fixture
def invalid_post_response(valid_post_request, url, post_data):
    post_data["form-0-price"] = "words"
    return valid_post_request(url, post_data)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def post_data(invalid_products):
    product_count = len(invalid_products)
    form_data = {
        "form-TOTAL_FORMS": product_count,
        "form-INITIAL_FORMS": product_count,
        "form-MAX_NUM_FORMS": product_count,
    }
    for i, product in enumerate(invalid_products):
        form_data.update({f"form-{i}-id": product.id, f"form-{i}-price": 556})
    return form_data


@pytest.fixture
def invalid_products(fnac_product_factory):
    return [fnac_product_factory.create(price=None) for i in range(5)]


@pytest.fixture
def valid_products(fnac_product_factory):
    return [fnac_product_factory.create() for i in range(5)]


@pytest.fixture
def irrelevant_products(fnac_product_factory):
    return [
        fnac_product_factory.create(created=True),
        fnac_product_factory.create(do_not_create=True),
    ]


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


@pytest.mark.django_db
def test_logged_in_group_post(
    group_logged_in_client, invalid_products, valid_products, url, post_data
):
    response = group_logged_in_client.post(url, post_data)
    assert response.status_code == 302


def test_heading(valid_get_response_content):
    text = "<h1>Missing Prices</h1>"
    assert text in valid_get_response_content


@pytest.mark.django_db
def test_products_with_missing_price_displaid(
    irrelevant_products, invalid_products, valid_products, valid_get_response_content
):
    for product in invalid_products:
        assert product.sku in valid_get_response_content
        assert product.name in valid_get_response_content


@pytest.mark.django_db
def test_products_with_price_not_displaid(
    irrelevant_products, invalid_products, valid_products, valid_get_response_content
):
    for product in valid_products:
        assert product.sku not in valid_get_response_content
        assert product.name not in valid_get_response_content


@pytest.mark.django_db
def test_products_that_are_not_relevent_are_not_displaid(
    irrelevant_products, valid_products, invalid_products, valid_get_response_content
):
    for product in irrelevant_products:
        assert product.sku not in valid_get_response_content
        assert product.name not in valid_get_response_content


@pytest.mark.django_db
def test_post_status_code(valid_products, invalid_products, valid_post_response):
    assert valid_post_response.status_code == 302


@pytest.mark.django_db
def test_post_success_url(valid_products, invalid_products, valid_post_response):
    assert valid_post_response.url == reverse("fnac:index")


@pytest.mark.django_db
def test_prices_updated(valid_products, invalid_products, valid_post_response):
    for product in invalid_products:
        product.refresh_from_db()
        assert product.price == 556


@pytest.mark.django_db
def test_invalid_post_status_code(
    valid_products, invalid_products, invalid_post_response
):
    assert invalid_post_response.status_code == 200
    assert "price" in invalid_post_response.content.decode("utf8")
