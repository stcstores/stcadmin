from pathlib import Path

import openpyxl
import pytest


@pytest.fixture
def url():
    return "/fnac/created_products/"


@pytest.fixture(scope="module")
def product_export_path():
    return Path(__file__).parent / "mirakl_product_export.xlsx"


@pytest.fixture(scope="module")
def product_export_worksheet(product_export_path):
    return openpyxl.load_workbook(product_export_path)["Data"]


@pytest.fixture(scope="module")
def export_skus(product_export_worksheet):
    skus = []
    for row_number, row in enumerate(product_export_worksheet.rows):
        if row_number < 2:
            continue
        skus.append(list(row)[1].value)
    return skus


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def products(fnac_product_factory, export_skus):
    return [fnac_product_factory.create(sku=sku, created=False) for sku in export_skus]


@pytest.fixture
def valid_post_response(valid_post_request, product_export_path, url):
    with open(product_export_path, "rb") as f:
        return valid_post_request(url, {"export_file": f})


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


def test_logged_in_group_post(valid_post_response):
    assert valid_post_response.status_code == 302


@pytest.mark.django_db
def test_products_marked_created(products, valid_post_response):
    for product in products:
        product.refresh_from_db()
        assert product.created is True
