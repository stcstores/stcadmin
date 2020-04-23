import csv

import pytest

from fnac.models import Comment
from fnac.models.offer_update import create_offer_update_export


@pytest.fixture
def comment_text():
    return "Shipping Time\n2 Working Days"


@pytest.fixture
def comment(comment_text):
    return Comment.objects.set_comment_text(comment_text)


@pytest.fixture
def offer_file_contents(comment):
    csv_string = create_offer_update_export()
    csv_string.seek(0)
    reader = csv.reader(csv_string, delimiter=";")
    return list(reader)


@pytest.fixture
def product(fnac_product_factory):
    return fnac_product_factory.create(created=True)


@pytest.fixture
def product_without_price(fnac_product_factory):
    return fnac_product_factory.create(created=True, price=None)


@pytest.fixture
def export_row(product, offer_file_contents):
    return offer_file_contents[1]


@pytest.fixture
def invalid_product(fnac_product_factory):
    return fnac_product_factory.create(created=False)


@pytest.mark.django_db
def test_response_header(product, offer_file_contents):
    assert offer_file_contents[0][0] == "id-produit"


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
    product, invalid_product, offer_file_contents, export_row
):
    assert len(offer_file_contents) == 2
    assert invalid_product.sku not in export_row


@pytest.mark.django_db
def test_product_without_price_is_not_exported(
    product, product_without_price, offer_file_contents, export_row
):
    assert len(offer_file_contents) == 2
    assert product_without_price.sku not in export_row
