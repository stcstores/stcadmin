from io import BytesIO

import openpyxl
import pytest


@pytest.fixture
def url():
    return "/fnac/new_product_file/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    workbook = openpyxl.load_workbook(filename=BytesIO(valid_get_response.content))
    return workbook


@pytest.fixture
def product(fnac_product_factory, translation_factory):
    product = fnac_product_factory.create()
    translation_factory.create(product=product)
    return product


@pytest.fixture
def export_row(product, valid_get_response_content):
    worksheet = valid_get_response_content.active
    return [_.value for _ in list(worksheet.rows)[2]]


@pytest.fixture
def invalid_product(fnac_product_factory):
    return fnac_product_factory.create()


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


@pytest.mark.django_db
def test_response_header(product, valid_get_response_content):
    worksheet = valid_get_response_content.active
    assert list(worksheet.rows)[0][0].value == "Typologie"
    assert list(worksheet.rows)[1][0].value == "Typology"


@pytest.mark.django_db
def test_response_row(product, export_row):
    cell_values = [
        product.sku,
        product.translation.name,
        product.translation.description,
        product.translation.description,
        "Accessoires",
        product.fnac_range.category.french,
        product.barcode,
        product.brand,
        product.translation.colour,
        product.french_size.name,
        product.image_1,
        product.image_2,
        product.image_3,
    ]
    for value in cell_values:
        assert value in export_row


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name,expected",
    [
        ("Non Matching", "Accessoires"),
        ("plush", "Peluche"),
        ("sticker", "Autocollant / Magnets"),
    ],
)
def test_format_is_set(
    name, expected, fnac_product_factory, translation_factory, valid_get_request, url
):
    product = fnac_product_factory(name=name)
    translation_factory.create(product=product)
    response = valid_get_request(url)
    worksheet = openpyxl.load_workbook(filename=BytesIO(response.content)).active
    row = [_.value for _ in list(worksheet.rows)[2]]
    assert expected in row


@pytest.mark.django_db
def test_invaild_product_is_not_exported(
    product, invalid_product, valid_get_response_content, export_row
):
    assert len(list(valid_get_response_content.active.rows)) == 3
    assert invalid_product.sku not in export_row
