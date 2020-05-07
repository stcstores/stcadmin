import pytest

from itd.models import ITDProduct


@pytest.fixture
def mock_product(mock_orders):
    return mock_orders[0].products[0]


@pytest.fixture
def existing_order(itd_order_factory):
    return itd_order_factory.create()


@pytest.mark.django_db
def test_create_from_dispatch_sets_order(mock_product, existing_order):
    product = ITDProduct.objects.create_from_dispatch(existing_order, mock_product)
    assert product.order == existing_order


@pytest.mark.django_db
def test_create_from_dispatch_sets_sku(mock_product, existing_order):
    product = ITDProduct.objects.create_from_dispatch(existing_order, mock_product)
    assert product.sku == mock_product.sku


@pytest.mark.django_db
def test_create_from_dispatch_sets_name(mock_product, existing_order):
    product = ITDProduct.objects.create_from_dispatch(existing_order, mock_product)
    assert product.name == mock_product.product_name


@pytest.mark.django_db
def test_create_from_dispatch_sets_price(mock_product, existing_order):
    mock_product.price = 5.50
    product = ITDProduct.objects.create_from_dispatch(existing_order, mock_product)
    assert product.price == 550


@pytest.mark.django_db
def test_create_from_dispatch_sets_weight(mock_product, existing_order):
    product = ITDProduct.objects.create_from_dispatch(existing_order, mock_product)
    assert product.weight == int(mock_product.per_item_weight)


@pytest.mark.django_db
def test_create_from_dispatch_sets_quantity(mock_product, existing_order):
    product = ITDProduct.objects.create_from_dispatch(existing_order, mock_product)
    assert product.quantity == mock_product.quantity
