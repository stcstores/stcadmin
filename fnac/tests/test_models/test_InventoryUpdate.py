from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from tabler import Table

from fnac import models


@pytest.fixture(scope="module")
def inventory_file():
    return Table(Path(__file__).parent / "test_inventory.xlsx")


@pytest.fixture(scope="module")
def mock_latest_inventory_file(inventory_file):
    with patch("fnac.models.ProductExport") as mock_product_export_model:
        mock_product_export = Mock()
        mock_product_export.as_table.return_value = inventory_file
        mock_product_export_model.latest_export.return_value = mock_product_export
        yield


@pytest.fixture(scope="module", autouse=True)
def import_test_inventory(django_db_blocker, mock_latest_inventory_file):
    with django_db_blocker.unblock():
        models.update_inventory()


@pytest.fixture
def created_fnac_range(inventory_file):
    return models.FnacRange.objects.get(sku=inventory_file[0]["RNG_SKU"])


@pytest.fixture
def created_fnac_product(inventory_file):
    return models.FnacProduct.objects.get(sku=inventory_file[0]["VAR_SKU"])


def test_get_inventory_file():
    assert isinstance(models._InventoryUpdate.get_inventory_file(), Table)


@pytest.mark.django_db
def test_fnac_range_is_created(inventory_file):
    expected_skus = sorted(list(set(inventory_file.get_column("RNG_SKU"))))
    existing_skus = sorted(list(models.FnacRange.objects.values_list("sku", flat=True)))
    assert expected_skus == existing_skus


@pytest.mark.django_db
def test_fnac_products_are_created(inventory_file):
    expected_skus = sorted(list(inventory_file.get_column("VAR_SKU")))
    existing_skus = sorted(
        list(models.FnacProduct.objects.values_list("sku", flat=True))
    )
    assert expected_skus == existing_skus


@pytest.mark.django_db
def test_fnac_range_name_set(created_fnac_range, inventory_file):
    assert created_fnac_range.name == inventory_file[0]["RNG_Name"]


@pytest.mark.django_db
def test_fnac_range_category_is_null(created_fnac_range):
    assert created_fnac_range.category is None


@pytest.mark.django_db
def test_fnac_product_name_set(created_fnac_product, inventory_file):
    assert created_fnac_product.name == inventory_file[0]["VAR_Name"]


@pytest.mark.django_db
def test_fnac_product_barcode_set(created_fnac_product, inventory_file):
    assert created_fnac_product.barcode == inventory_file[0]["VAR_Barcode"]


@pytest.mark.django_db
def test_fnac_product_description_set(created_fnac_product, inventory_file):
    assert created_fnac_product.description == inventory_file[0]["VAR_Description"]


@pytest.mark.django_db
def test_fnac_product_colour_set(created_fnac_product, inventory_file):
    assert created_fnac_product.colour == inventory_file[0]["OPT_Colour_DRD"]


@pytest.mark.django_db
def test_fnac_product_brand_set(created_fnac_product, inventory_file):
    assert created_fnac_product.brand == inventory_file[0]["OPT_Brand"]


@pytest.mark.django_db
def test_fnac_product_english_size_set(created_fnac_product, inventory_file):
    assert created_fnac_product.english_size == inventory_file[0]["OPT_Size_DRD"]


@pytest.mark.django_db
def test_fnac_product_stock_level_set(created_fnac_product, inventory_file):
    assert created_fnac_product.stock_level == int(inventory_file[0]["VAR_Stock"])


@pytest.mark.django_db
def test_fnac_product_french_size_is_null(created_fnac_product):
    assert created_fnac_product.french_size is None


@pytest.mark.django_db
def test_fnac_product_price_is_null(created_fnac_product):
    assert created_fnac_product.price is None


@pytest.mark.django_db
def test_fnac_do_not_create_is_false(created_fnac_product):
    assert created_fnac_product.do_not_create is False


@pytest.mark.django_db
def test_fnac_created_is_false(created_fnac_product):
    assert created_fnac_product.created is False


@pytest.mark.django_db
def test_fnac_range_is_updated(created_fnac_range, inventory_file):
    created_fnac_range.name = "Test Name"
    models.update_inventory()
    updated_range = models.FnacRange.objects.get(sku=created_fnac_range.sku)
    assert updated_range.name == inventory_file[0]["RNG_Name"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "barcode,expected",
    [
        (None, ""),
        ("8486512347864", "8486512347864"),
        ("965123487521", "0965123487521"),
        ("8486512347864 \n", "8486512347864"),
        ("965123487521,8486512347864,", "0965123487521"),
        ("3487521,8486512347864,", "8486512347864"),
        ("", ""),
    ],
)
def test_clean_barcode(barcode, expected):
    assert models._InventoryUpdate.clean_barcode(barcode) == expected
