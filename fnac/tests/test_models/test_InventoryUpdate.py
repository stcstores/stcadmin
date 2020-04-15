from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from tabler import Table

from fnac import models


@pytest.fixture()
def inventory_file():
    return Table(Path(__file__).parent / "test_inventory.xlsx")


@pytest.fixture()
def mock_latest_inventory_file(inventory_file):
    with patch(
        "fnac.models.inventory_update.ProductExport", autospec=True
    ) as mock_ProductExport:
        mock_product_export = Mock()
        mock_product_export.as_table.return_value = inventory_file
        mock_ProductExport.latest_export.return_value = mock_product_export
        yield


@pytest.fixture()
def import_test_inventory(db, mock_latest_inventory_file):
    models.update_inventory()


@pytest.fixture
def created_fnac_range(import_test_inventory, inventory_file):
    return models.FnacRange.objects.get(sku=inventory_file[0]["RNG_SKU"])


@pytest.fixture
def created_fnac_product(import_test_inventory, inventory_file):
    return models.FnacProduct.objects.get(sku=inventory_file[0]["VAR_SKU"])


def test_get_inventory_file(import_test_inventory,):
    inventory_file = models.inventory_update._InventoryUpdate.get_inventory_file()
    assert isinstance(inventory_file, Table)


def test_fnac_range_is_created(import_test_inventory, inventory_file):
    expected_skus = sorted(list(set(inventory_file.get_column("RNG_SKU"))))
    existing_skus = sorted(list(models.FnacRange.objects.values_list("sku", flat=True)))
    assert expected_skus == existing_skus


def test_fnac_products_are_created(import_test_inventory, inventory_file):
    expected_skus = sorted(list(inventory_file.get_column("VAR_SKU")))
    existing_skus = sorted(
        list(models.FnacProduct.objects.values_list("sku", flat=True))
    )
    assert expected_skus == existing_skus


def test_fnac_range_name_set(import_test_inventory, created_fnac_range, inventory_file):
    assert created_fnac_range.name == "Adults Christmas Reindeer Slippers"


def test_fnac_range_category_is_null(import_test_inventory, created_fnac_range):
    assert created_fnac_range.category is None


def test_fnac_product_name_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.name == "Adults Christmas Reindeer Slippers"


def test_fnac_product_barcode_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.barcode == "8944099045578"


def test_fnac_product_description_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.description == "\n".join(
        [
            "<ul>",
            " <li>",
            "  Adults unisex novelty Christmas slippers.",
            " </li>",
            " <li>",
            "  Upper = Low plush pile, Sole = pin dot grip.",
            "  <br/>",
            "  <br/>",
            "  For sizing in US and Australia please use outer sole measurements as a guide.",
            "  <br/>",
            "  <br/>",
            '  Small is approx UK 3-4, EU 36-37, Outer sole length 9.5"',
            "  <br/>",
            '  Medium is approx UK 5-6, EU 38-39, Outer sole length 10"',
            "  <br/>",
            '  Large is approx UK 7-8, EU 40-41, Outer sole length 10.5"',
            "  <br/>",
            '  XL is approx UK 9-10, EU 43-44, Outer sole length 11"',
            "  <br/>",
            '  XXL is approx UK 11-12, EU 45-46, Outer sole length 11.5"',
            " </li>",
            "</ul>",
        ]
    )


def test_fnac_product_colour_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.colour == ""


def test_fnac_product_colour_set_when_available(import_test_inventory,):
    assert models.FnacProduct.objects.get(sku="RU0-755-RPU").colour == "Black Trim"


def test_fnac_product_brand_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.brand == "Aucun"


def test_fnac_product_english_size_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.english_size == "Large (UK 7-8)"


def test_fnac_product_stock_level_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.stock_level == 0


def test_fnac_product_image_1_field_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.image_1 == "19796021.jpg"


def test_fnac_product_image_2_field_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.image_2 == "33125872.jpg"


def test_fnac_product_image_3_field_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.image_3 == ""


def test_fnac_product_image_4_field_set(
    import_test_inventory, created_fnac_product, inventory_file
):
    assert created_fnac_product.image_4 == ""


def test_fnac_product_french_size_is_null(import_test_inventory, created_fnac_product):
    assert created_fnac_product.french_size is None


def test_fnac_product_price_is_null(import_test_inventory, created_fnac_product):
    assert created_fnac_product.price is None


def test_fnac_do_not_create_is_false(import_test_inventory, created_fnac_product):
    assert created_fnac_product.do_not_create is False


def test_fnac_created_is_false(import_test_inventory, created_fnac_product):
    assert created_fnac_product.created is False


def test_fnac_range_is_updated(
    import_test_inventory, created_fnac_range, inventory_file
):
    created_fnac_range.name = "Test Name"
    models.update_inventory()
    updated_range = models.FnacRange.objects.get(sku=created_fnac_range.sku)
    assert updated_range.name == inventory_file[0]["RNG_Name"]


def test_colour_is_not_overwritten_by_inventory_update(
    import_test_inventory, inventory_file
):
    colour = "Grey"
    sku = inventory_file.get_column("VAR_SKU")[10]
    product = models.FnacProduct.objects.get(sku=sku)
    product.colour = colour
    product.save()
    models.update_inventory()
    product.refresh_from_db()
    assert product.colour == colour


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
def test_clean_barcode(import_test_inventory, barcode, expected):
    assert models.inventory_update._InventoryUpdate.clean_barcode(barcode) == expected


@pytest.mark.parametrize(
    "brand,expected",
    [
        ("Stock Inc", "Stock Inc"),
        ("", "Aucun"),
        (None, "Aucun"),
        ("Unbranded", "Aucun"),
    ],
)
def test_clean_brand(import_test_inventory, brand, expected):
    assert models.inventory_update._InventoryUpdate.clean_brand(brand) == expected


@pytest.mark.parametrize(
    "image_field_contents,expected",
    [
        ("9481616416.jpg", ["9481616416.jpg", "", "", ""]),
        (
            "9481616416.jpg|94816418916.jpg",
            ["9481616416.jpg", "94816418916.jpg", "", ""],
        ),
        (
            "9481616416.jpg|48941818949.jpg|94198418189.jpg",
            ["9481616416.jpg", "48941818949.jpg", "94198418189.jpg", ""],
        ),
        (
            "9481616416.jpg|81891849419.jpg|48941894981.jpg|89418948491.jpg",
            ["9481616416.jpg", "81891849419.jpg", "48941894981.jpg", "89418948491.jpg"],
        ),
        ("9481616416.jpg ", ["9481616416.jpg", "", "", ""]),
        (
            "9481616416.jpg|81891849419.jpg|48941894981.jpg|89418948491.jpg|98418949481.jpg",
            ["9481616416.jpg", "81891849419.jpg", "48941894981.jpg", "89418948491.jpg"],
        ),
        (
            " 9481616416.jpg | 48941818949.jpg | 94198418189.jpg \n",
            ["9481616416.jpg", "48941818949.jpg", "94198418189.jpg", ""],
        ),
        (None, ["", "", "", ""]),
        ("", ["", "", "", ""]),
    ],
)
def test_clean_images(import_test_inventory, image_field_contents, expected):
    assert (
        models.inventory_update._InventoryUpdate.clean_images(image_field_contents)
        == expected
    )


def test_update_inventory_accepts_update_file(import_test_inventory, inventory_file):
    sku = "999-999-999"
    inventory_file[0]["RNG_SKU"] = sku
    models.update_inventory(inventory_file=inventory_file)
    assert models.FnacRange.objects.filter(sku=sku).count() == 1
