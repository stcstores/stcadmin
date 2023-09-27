from unittest import mock

import pytest

from inventory.models import BaseProduct
from inventory.models.archive import Archiver


@pytest.fixture
def mock_stock_manager():
    with mock.patch("inventory.models.archive.StockManager") as mock_stock_manager:
        yield mock_stock_manager


@pytest.mark.django_db
def test_get_product_queryset_returns_product(product_factory):
    product = product_factory.create(is_end_of_line=True, is_archived=False)
    qs = Archiver.get_product_queryset()
    assert product in qs


@pytest.mark.django_db
def test_get_product_queryset_does_not_return_archived_products(product_factory):
    product = product_factory.create(is_end_of_line=True, is_archived=True)
    qs = Archiver.get_product_queryset()
    assert product not in qs


@pytest.mark.django_db
def test_get_product_queryset_does_not_return_products_not_EOL(product_factory):
    product = product_factory.create(is_end_of_line=False, is_archived=False)
    qs = Archiver.get_product_queryset()
    assert product not in qs


@pytest.mark.django_db
def test_get_product_queryset_does_not_return_product_with_not_processed_fba_order(
    product_factory, fba_order_factory
):
    product = product_factory.create(is_end_of_line=True, is_archived=False)
    fba_order_factory.create(product=product, not_processed=True)
    qs = Archiver.get_product_queryset()
    assert product not in qs


@pytest.mark.django_db
def test_get_product_queryset_does_not_return_product_with_on_hold_fba_order(
    product_factory, fba_order_factory
):
    product = product_factory.create(is_end_of_line=True, is_archived=False)
    fba_order_factory.create(product=product, on_hold=True)
    qs = Archiver.get_product_queryset()
    assert product not in qs


@pytest.mark.django_db
def test_get_product_queryset_does_not_return_product_with_awaiting_collection_booking_fba_order(
    product_factory, fba_order_factory
):
    product = product_factory.create(is_end_of_line=True, is_archived=False)
    fba_order_factory.create(product=product, awaiting_booking=True)
    qs = Archiver.get_product_queryset()
    assert product not in qs


@pytest.mark.django_db
def test_get_product_queryset_does_not_return_product_with_printed_fba_order(
    product_factory, fba_order_factory
):
    product = product_factory.create(is_end_of_line=True, is_archived=False)
    fba_order_factory.create(product=product, printed=True)
    qs = Archiver.get_product_queryset()
    assert product not in qs


@pytest.mark.django_db
def test_get_product_queryset_returns_product_with_fulfilled_fba_order(
    product_factory, fba_order_factory
):
    product = product_factory.create(is_end_of_line=True, is_archived=False)
    fba_order_factory.create(product=product, fulfilled=True)
    qs = Archiver.get_product_queryset()
    assert product in qs


@pytest.mark.django_db
def test_filter_out_of_stock_products_returns_out_of_stock_products(
    mock_stock_manager, product_factory
):
    in_stock_product = product_factory.create()
    out_of_stock_product = product_factory.create()
    mock_stock_manager.get_stock_levels.return_value = {
        in_stock_product.sku: mock.Mock(available=1),
        out_of_stock_product.sku: mock.Mock(available=0),
    }
    qs = BaseProduct.objects.filter(
        id__in=(in_stock_product.id, out_of_stock_product.id)
    )
    returned_ptoducts = Archiver.filter_out_of_stock_products(qs)
    assert in_stock_product not in returned_ptoducts
    assert out_of_stock_product in returned_ptoducts


@pytest.mark.django_db
@mock.patch("inventory.models.archive.Archiver.filter_out_of_stock_products")
@mock.patch("inventory.models.archive.Archiver.get_product_queryset")
def test_get_archivable_products_calls_get_product_queryset(
    mock_get_product_quyerset, mock_filter_out_of_stock_products
):
    Archiver.get_archivable_products()
    mock_get_product_quyerset.assert_called_once_with()


@pytest.mark.django_db
@mock.patch("inventory.models.archive.Archiver.filter_out_of_stock_products")
@mock.patch("inventory.models.archive.Archiver.get_product_queryset")
def test_get_archivable_products_calls_filter_out_of_stock_products(
    mock_get_product_quyerset, mock_filter_out_of_stock_products
):
    Archiver.get_archivable_products()
    mock_get_product_quyerset, mock_filter_out_of_stock_products
    mock_filter_out_of_stock_products.assert_called_once_with(
        mock_get_product_quyerset.return_value
    )


@pytest.mark.django_db
@mock.patch("inventory.models.archive.Archiver.get_archivable_products")
def test_archivable_products_set_archive_method_is_called(mock_get_archivable_products):
    products = [mock.Mock(), mock.Mock(), mock.Mock()]
    mock_get_archivable_products.return_value = products
    Archiver.archive_products()
    for product in products:
        product.set_archived.called_once_with()
