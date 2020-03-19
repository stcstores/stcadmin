import csv
from io import StringIO

import pytest

from fnac.models import Comment


@pytest.fixture
def comment_text():
    return "Shipping Time\n2 Working Days"


@pytest.fixture
def comment(comment_text):
    return Comment.objects.set_comment_text(comment_text)


@pytest.fixture
def url():
    return "/fnac/update_file/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(comment, valid_get_response):
    reader = csv.reader(
        StringIO(valid_get_response.content.decode("utf8")), delimiter=";"
    )
    return list(reader)


@pytest.fixture
def product(fnac_product_factory, translation_factory):
    product = fnac_product_factory.create(created=True)
    return product


@pytest.fixture
def export_row(product, valid_get_response_content):
    return valid_get_response_content[1]


@pytest.fixture
def invalid_product(fnac_product_factory):
    return fnac_product_factory.create(created=False)


def test_logged_out_get_method(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_get(comment, valid_get_response):
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
    assert valid_get_response_content[0][0] == "id-produit"


@pytest.mark.django_db
def test_response_row(product, comment, export_row, comment_text):
    cell_values = [
        product.barcode,
        product.sku,
        str(product.stock_level),
        f"{float(product.price)/100:.2f}",
        comment_text,
    ]
    for value in cell_values:
        assert value in export_row


@pytest.mark.django_db
def test_invaild_product_is_not_exported(
    product, invalid_product, valid_get_response_content, export_row
):
    assert len(valid_get_response_content) == 2
    assert invalid_product.sku not in export_row
