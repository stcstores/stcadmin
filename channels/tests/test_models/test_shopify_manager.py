from unittest import mock

import pytest
from shopify_api_py.exceptions import ProductNotFoundError

from channels.models.shopify_models import ShopifyManager


@pytest.fixture
def mock_shopify_api():
    with mock.patch(
        "channels.models.shopify_models.shopify_manager.shopify_api_py"
    ) as m:
        yield m


@pytest.fixture
def mock_time():
    with mock.patch("channels.models.shopify_models.shopify_manager.time") as m:
        yield m


def test_request_pause_attribute():
    assert ShopifyManager.REQUEST_PAUSE == 0.51


def test_active_attribute():
    assert ShopifyManager.ACTIVE == "active"


def test_draft_attribute():
    assert ShopifyManager.DRAFT == "draft"


@pytest.fixture
def mock_get_product():
    with mock.patch(
        "channels.models.shopify_models.shopify_manager.ShopifyManager._get_product"
    ) as m:
        yield m


@pytest.fixture
def mock_set_product_status():
    with mock.patch(
        "channels.models.shopify_models.shopify_manager.ShopifyManager._set_product_status"
    ) as m:
        yield m


# @pytest.fixture
# def mock_get_products():
#     with mock.patch(
#         "channels.models.shopify_models.shopify_manager.ShopifyManager._get_products"
#     ) as m:
#         yield m


@pytest.fixture
def product_id():
    return 49235708239


@pytest.fixture
def collection_id():
    return 898903567340


@pytest.fixture
def inventory_item_id():
    return 3284097234560


@pytest.fixture
def variant_id():
    return 62342390800


@pytest.fixture
def location_id():
    return 17560843760


def test_product_exists_method(mock_get_product, product_id):
    value = ShopifyManager.product_exists(product_id)
    mock_get_product.assert_called_once_with(product_id)
    assert value is True


def test_product_exists_method_with_non_existant_product(mock_get_product, product_id):
    mock_get_product.side_effect = ProductNotFoundError(product_id)
    value = ShopifyManager.product_exists(product_id)
    mock_get_product.assert_called_once_with(product_id)
    assert value is False


def test_get_collections_method(mock_shopify_api):
    value = ShopifyManager.get_collections()
    mock_shopify_api.products.get_all_custom_collections.assert_called_once_with()
    assert value == mock_shopify_api.products.get_all_custom_collections.return_value


def test_add_product_to_collection_method(mock_shopify_api, product_id, collection_id):
    ShopifyManager.add_product_to_collection(
        product_id=product_id, collection_id=collection_id
    )
    mock_shopify_api.products.add_product_to_collection.assert_called_once_with(
        product_id=product_id, collection_id=collection_id
    )


def test_remove_product_from_collection_method(
    mock_shopify_api, product_id, collection_id
):
    ShopifyManager.remove_product_from_collection(
        product_id=product_id, collection_id=collection_id
    )
    mock_shopify_api.products.remove_product_from_collection.assert_called_once_with(
        product_id=product_id, collection_id=collection_id
    )


def test_remove_product_from_all_collections_method(mock_shopify_api, product_id):
    collects = [mock.Mock() for _ in range(3)]
    mock_shopify_api.products.shopify.Collect.find.return_value = collects
    ShopifyManager.remove_product_from_all_collections(product_id)
    mock_shopify_api.products.shopify.Collect.find.assert_called_once_with(
        product_id=product_id
    )
    for collect in collects:
        collect.destroy.assert_called_once_with()


def test_get_product_method(mock_shopify_api, product_id):
    value = ShopifyManager._get_product(product_id)
    mock_shopify_api.products.get_product_by_id.assert_called_once_with(
        product_id=product_id
    )
    assert value == mock_shopify_api.products.get_product_by_id.return_value


def test_get_variant_method(mock_shopify_api, variant_id):
    value = ShopifyManager._get_variant(variant_id)
    mock_shopify_api.products.get_variant_by_id.assert_called_once_with(
        variant_id=variant_id
    )
    assert value == mock_shopify_api.products.get_variant_by_id.return_value


def test_get_inventory_item_method(mock_shopify_api, inventory_item_id):
    value = ShopifyManager._get_inventory_item(inventory_item_id)
    mock_shopify_api.products.get_inventory_item_by_id.assert_called_once_with(
        inventory_item_id=inventory_item_id
    )
    assert value == mock_shopify_api.products.get_inventory_item_by_id.return_value


def test_get_products_method(mock_shopify_api, product_id):
    value = ShopifyManager._get_products()
    mock_shopify_api.products.get_all_products.assert_called_once_with()
    assert value == mock_shopify_api.products.get_all_products.return_value


def test_get_location_id_method(mock_shopify_api, variant_id):
    mock_shopify_api.locations.get_inventory_locations.return_vaue = [mock.Mock()]
    value = ShopifyManager._get_location_id()
    mock_shopify_api.locations.get_inventory_locations.assert_called_once_with()
    assert (
        value == mock_shopify_api.locations.get_inventory_locations.return_value[0].id
    )


def test_update_variant_stock_method_with_no_change(
    mock_shopify_api, location_id, mock_time
):
    variant = mock.Mock(inventory_quantity=6)
    stock_levels = {variant.sku: 6}
    ShopifyManager._update_variant_stock(
        variant=variant, location_id=location_id, stock_levels=stock_levels
    )
    mock_shopify_api.products.update_variant_stock.assert_not_called()
    mock_time.sleep.assert_not_called()


def test_update_variant_stock_method(mock_shopify_api, location_id, mock_time):
    variant = mock.Mock(inventory_quantity=8)
    stock_levels = {variant.sku: 6}
    ShopifyManager._update_variant_stock(
        variant=variant, location_id=location_id, stock_levels=stock_levels
    )
    mock_shopify_api.products.update_variant_stock.assert_called_once_with(
        variant=variant, new_stock_level=6, location_id=location_id
    )
    mock_time.sleep.assert_called_once_with(ShopifyManager.REQUEST_PAUSE)


def test_update_product_status_method_sets_draft(mock_set_product_status):
    variants = [mock.Mock(inventory_quantity=0) for _ in range(3)]
    product = mock.Mock(status=ShopifyManager.ACTIVE, variants=variants)
    ShopifyManager._update_product_status(product)
    mock_set_product_status.assert_called_once_with(product, ShopifyManager.DRAFT)


def test_update_product_status_method_sets_active(mock_set_product_status):
    variants = [mock.Mock(inventory_quantity=1) for _ in range(3)]
    product = mock.Mock(status=ShopifyManager.DRAFT, variants=variants)
    ShopifyManager._update_product_status(product)
    mock_set_product_status.assert_called_once_with(product, ShopifyManager.ACTIVE)


def test_update_product_status_method_with_active_in_stock_product(
    mock_set_product_status,
):
    variants = [mock.Mock(inventory_quantity=1) for _ in range(3)]
    product = mock.Mock(status=ShopifyManager.ACTIVE, variants=variants)
    ShopifyManager._update_product_status(product)
    mock_set_product_status.assert_not_called()


def test_update_product_status_method_with_out_of_stock_draft(mock_set_product_status):
    variants = [mock.Mock(inventory_quantity=1) for _ in range(3)]
    product = mock.Mock(status=ShopifyManager.ACTIVE, variants=variants)
    ShopifyManager._update_product_status(product)
    mock_set_product_status.assert_not_called()


def test_set_product_status_method(mock_time):
    product = mock.Mock()
    status = ShopifyManager.ACTIVE
    ShopifyManager._set_product_status(product, status)
    assert product.status == status
    product.save.assert_called_once_with()
    mock_time.sleep.assert_called_once_with(ShopifyManager.REQUEST_PAUSE)


def test_hide_product_method(mock_shopify_api):
    product = mock.Mock()
    ShopifyManager._hide_product(product)
    assert product.status == ShopifyManager.DRAFT
    product.save.assert_called_once_with()


def test_unhide_product_method(mock_shopify_api):
    product = mock.Mock()
    ShopifyManager._unhide_product(product)
    assert product.status == ShopifyManager.ACTIVE
    product.save.assert_called_once_with()
