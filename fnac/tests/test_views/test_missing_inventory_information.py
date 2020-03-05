import pytest


@pytest.fixture
def url():
    return "/fnac/missing_inventory_info/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def invalid_products(fnac_product_factory):
    return [
        fnac_product_factory.create(description=""),
        fnac_product_factory.create(barcode=""),
        fnac_product_factory.create(image_1=""),
    ]


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


def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


def test_heading(valid_get_response_content):
    text = "<h1>Missing Inventory Information</h1>"
    assert text in valid_get_response_content


@pytest.mark.django_db
def test_products_with_missing_info_displaid(
    irrelevant_products, invalid_products, valid_products, valid_get_response_content
):
    for product in invalid_products:
        assert product.sku in valid_get_response_content
        assert product.name in valid_get_response_content


@pytest.mark.django_db
def test_products_with_valid_info_not_displaid(
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
