import pytest
from django.shortcuts import reverse

from fnac import models


@pytest.fixture
def url():
    return "/fnac/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def products(
    fnac_range_factory, fnac_product_factory, size_factory, translation_factory
):
    products = [
        fnac_product_factory.create(),
        fnac_product_factory.create(created=True),
        fnac_product_factory.create(description=""),
        fnac_product_factory.create(price=None),
        fnac_product_factory.create(french_size=None, price=556),
        fnac_product_factory.create(french_size=None, price=None),
        fnac_product_factory.create(
            fnac_range=fnac_range_factory.create(category=None)
        ),
        fnac_product_factory.create(do_not_create=True),
        fnac_product_factory.create(stock_level=0),
        fnac_product_factory.create(),
    ]
    for product in products[1:]:
        translation_factory.create(product=product)
    return products


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


def test_url_heading(valid_get_response_content):
    assert "<h1>FNAC</h1>" in valid_get_response_content


def test_links_to_missing_inventory_info(valid_get_response_content):
    assert valid_get_response_content.count(reverse("fnac:missing_inventory_info")) == 2


def test_links_to_missing_price_size(valid_get_response_content):
    assert valid_get_response_content.count(reverse("fnac:missing_price_size")) == 2


def test_links_to_missing_category(valid_get_response_content):
    assert valid_get_response_content.count(reverse("fnac:missing_category")) == 2


def test_links_to_translations(valid_get_response_content):
    assert valid_get_response_content.count(reverse("fnac:translations")) == 2


@pytest.mark.django_db
def test_links_to_new_product_file(products, valid_get_response_content):
    assert reverse("fnac:new_product_file") in valid_get_response_content


def test_does_not_link_to_product_file_if_no_valid_products_exist(
    valid_get_response_content,
):
    assert reverse("fnac:new_product_file") not in valid_get_response_content


@pytest.mark.django_db
def test_created_count_in_context(products, valid_get_response):
    assert valid_get_response.context["created_product_count"] == 1


@pytest.mark.django_db
def test_missing_inventory_info_count_in_context(products, valid_get_response):
    assert valid_get_response.context["missing_inventory_info_count"] == 1


@pytest.mark.django_db
def test_missing_category_count_in_context(products, valid_get_response):
    assert valid_get_response.context["missing_category_count"] == 1


@pytest.mark.django_db
def test_missing_price_size_count_in_context(products, valid_get_response):
    assert valid_get_response.context["missing_price_size_count"] == 3


@pytest.mark.django_db
def test_do_not_create_count_in_context(products, valid_get_response):
    assert valid_get_response.context["do_not_create_count"] == 1


@pytest.mark.django_db
def test_out_of_stock_count_in_context(products, valid_get_response):
    assert valid_get_response.context["out_of_stock_count"] == 1


@pytest.mark.django_db
def test_missing_translations_count_in_context(products, valid_get_response):
    assert valid_get_response.context["missing_translations_count"] == 1


@pytest.mark.django_db
def test_ready_to_create_count_in_context(products, valid_get_response):
    print(products)
    print(models.FnacProduct.objects.ready_to_create())
    assert valid_get_response.context["ready_to_create_count"] == 1
