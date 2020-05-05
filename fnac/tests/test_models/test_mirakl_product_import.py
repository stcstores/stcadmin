from pathlib import Path

import openpyxl
import pytest

from fnac.models.mirakl_product_import import import_mirakl_products


@pytest.fixture(scope="module")
def product_export_path():
    return Path(__file__).parent / "mirakl_product_export.xlsx"


@pytest.fixture(scope="module")
def product_export_workbook(product_export_path):
    return openpyxl.load_workbook(product_export_path)


@pytest.fixture(scope="module")
def export_skus(product_export_workbook):
    skus = []
    for row_number, row in enumerate(product_export_workbook["Data"].rows):
        if row_number < 2:
            continue
        skus.append(list(row)[1].value)
    return skus


@pytest.fixture
def products(fnac_product_factory, export_skus):
    return [fnac_product_factory.create(sku=sku, created=False) for sku in export_skus]


@pytest.mark.django_db
def test_products_marked_created(products, product_export_path):
    import_mirakl_products(product_export_path)
    for product in products:
        product.refresh_from_db()
        assert product.created is True
