from unittest import mock

import pytest

from channels.models.shopify_models import ShopifyCollection


@pytest.fixture
def shopify_collection(shopify_collection_factory):
    return shopify_collection_factory.create()


@pytest.mark.django_db
def test_full_clean(shopify_collection):
    assert shopify_collection.full_clean() is None


@pytest.mark.django_db
def test_has_name_attribute(shopify_collection):
    assert isinstance(shopify_collection.name, str)


@pytest.mark.django_db
def test_has_collection_id_attribute(shopify_collection):
    assert isinstance(shopify_collection.collection_id, int)


# Test Methods


@pytest.mark.django_db
def test_str_method(shopify_collection):
    assert str(shopify_collection) == shopify_collection.name


# Test Manager Methods


@pytest.fixture
def mock_shopify_manager():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyManager"
    ) as m:
        yield m


@pytest.mark.django_db
def test_update_collections_calls_get_collections(mock_shopify_manager):
    ShopifyCollection.objects.update_collections()
    mock_shopify_manager.get_collections.assert_called_once_with()


@pytest.mark.django_db
def test_update_collections_creates_collection(mock_shopify_manager):
    mock_shopify_manager.get_collections.return_value = [
        mock.Mock(id=123, title="Name")
    ]
    ShopifyCollection.objects.update_collections()
    assert ShopifyCollection.objects.filter(collection_id=123, name="Name").exists()


@pytest.mark.django_db
def test_update_collections_updates_collection(
    mock_shopify_manager, shopify_collection
):
    mock_shopify_manager.get_collections.return_value = [
        mock.Mock(id=shopify_collection.collection_id, title="Name")
    ]
    ShopifyCollection.objects.update_collections()
    shopify_collection.refresh_from_db()
    assert shopify_collection.name == "Name"


@pytest.mark.django_db
def test_update_collections_deletes_collection(
    mock_shopify_manager, shopify_collection
):
    mock_shopify_manager.get_collections.return_value = []
    ShopifyCollection.objects.update_collections()
    with pytest.raises(ShopifyCollection.DoesNotExist):
        shopify_collection.refresh_from_db()
