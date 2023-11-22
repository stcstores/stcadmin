from unittest import mock

import pytest

from purchases.forms import UpdateProductPurchaseForm


@pytest.fixture
def mock_stock_manager():
    with mock.patch("purchases.forms.StockManager") as m:
        yield m


@pytest.fixture
def new_quantity():
    return 15


@pytest.fixture
def purchase(product_purchase_factory, new_quantity):
    return product_purchase_factory.create(quantity=new_quantity)


@pytest.mark.django_db
def test_updates_quantity(purchase):
    form = UpdateProductPurchaseForm({"quantity": 5}, instance=purchase)
    assert form.is_valid()
    form.save()
    purchase.refresh_from_db()
    assert purchase.quantity == 5


@pytest.mark.django_db
@pytest.mark.parametrize(
    "original_quantity,new_quantity,old_stock_level,new_stock_level",
    ((15, 5, 18, 28), (1, 1, 1, 1), (5, 15, 18, 8)),
)
def test_update_stock_level_method(
    original_quantity,
    new_quantity,
    old_stock_level,
    new_stock_level,
    mock_stock_manager,
    product_purchase_factory,
):
    purchase = product_purchase_factory.create(quantity=original_quantity)
    mock_stock_manager.get_stock_level.return_value = old_stock_level
    form = UpdateProductPurchaseForm({"quantity": new_quantity}, instance=purchase)
    assert form.is_valid()
    form.save()
    form.update_stock_level()
    mock_stock_manager.get_stock_level.assert_called_once_with(purchase.product)
    mock_stock_manager.set_stock_level.assert_called_once_with(
        product=purchase.product,
        user=purchase.purchased_by.stcadmin_user,
        new_stock_level=new_stock_level,
        change_source=f"Staff purchase update by {purchase.purchased_by}",
    )


@pytest.mark.django_db
def test_update_stock_level_method_raises_for_exception_getting_stock_level(
    mock_stock_manager, purchase
):
    mock_stock_manager.get_stock_level.side_effect = Exception
    form = UpdateProductPurchaseForm({"quantity": 5}, instance=purchase)
    assert form.is_valid()
    form.save()
    with pytest.raises(Exception):
        form.update_stock_level()


@pytest.mark.django_db
def test_update_stock_level_method_raises_for_exception_setting_stock_level(
    mock_stock_manager, purchase
):
    mock_stock_manager.get_stock_level.return_value = 18
    mock_stock_manager.set_stock_level.side_effect = Exception
    form = UpdateProductPurchaseForm({"quantity": 5}, instance=purchase)
    assert form.is_valid()
    form.save()
    with pytest.raises(Exception):
        form.update_stock_level()


@pytest.mark.django_db
def test_update_stock_level_method_raises_for_stock_less_than_zero(
    mock_stock_manager, purchase
):
    mock_stock_manager.get_stock_level.return_value = 0
    form = UpdateProductPurchaseForm({"quantity": 16}, instance=purchase)
    assert form.is_valid()
    form.save()
    with pytest.raises(Exception):
        form.update_stock_level()
