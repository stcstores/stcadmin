from io import BytesIO

import openpyxl
import pytest


@pytest.fixture
def url():
    return "/fnac/translations_export/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    workbook = openpyxl.load_workbook(filename=BytesIO(valid_get_response.content))
    return workbook


@pytest.fixture
def products_with_translation(fnac_product_factory, translation_factory):
    products = [fnac_product_factory.create() for i in range(5)]
    for product in products:
        translation_factory.create(product=product)
    return products


@pytest.fixture
def products_without_translation(fnac_product_factory):
    return [fnac_product_factory.create() for i in range(5)]


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


def test_response_header(valid_get_response_content):
    worksheet = valid_get_response_content.active
    assert [_.value for _ in list(worksheet.rows)[0]] == [
        "ID",
        "SKU",
        "Title",
        "Colour",
        "Description",
        "¬",
    ]


@pytest.mark.django_db
def test_response_row(products_without_translation, valid_get_response_content):
    worksheet = valid_get_response_content.active
    rows = [[_.value for _ in row] for row in list(worksheet.rows)]
    for prodcut in products_without_translation:
        assert [
            products_without_translation[0].id,
            products_without_translation[0].sku,
            products_without_translation[0].name,
            products_without_translation[0].colour,
            products_without_translation[0].description,
            "¬",
        ] in rows


@pytest.mark.django_db
def test_only_products_without_translation_are_exported(
    products_without_translation, products_with_translation, valid_get_response_content
):
    worksheet = valid_get_response_content.active
    assert len(list(worksheet.rows)) == len(products_without_translation) + 1
    sku_column = [row[0].value for row in list(worksheet.rows)[1:]]
    product_ids = [product.id for product in products_without_translation]
    assert sorted(sku_column) == sorted(product_ids)


@pytest.fixture
def product_without_colour(fnac_product_factory):
    return fnac_product_factory.create(colour="")


@pytest.mark.django_db
def test_null_colours_are_replaced(product_without_colour, valid_get_response_content):
    worksheet = valid_get_response_content.active
    assert list(worksheet.rows)[1][3].value == "None"
