from unittest import mock

import pytest

from purchases.forms import CreateProductPurchaseForm


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def purchaser(staff_factory):
    return staff_factory.create()


@pytest.fixture
def form_data(purchaser, product):
    return {"purchaser": purchaser.id, "product_id": product.id, "quantity": 2}


@pytest.fixture
def mock_purchase_model():
    with mock.patch("purchases.forms.models.ProductPurchase") as mock_purchase_model:
        yield mock_purchase_model


@pytest.fixture
def purchase(product_purchase_factory):
    return product_purchase_factory.build()


@pytest.fixture
def saved_form(purchase):
    form = CreateProductPurchaseForm()
    form.instance = purchase
    return form


def test_has_purchaser_field():
    assert "purchaser" in CreateProductPurchaseForm().fields


def test_has_product_field():
    assert "product_id" in CreateProductPurchaseForm().fields


def test_has_quantity_field():
    assert "quantity" in CreateProductPurchaseForm().fields


@pytest.mark.django_db
def test_form_validation(form_data):
    form = CreateProductPurchaseForm(form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_purchaser_in_cleaned_data(purchaser, form_data):
    form = CreateProductPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["purchaser"] == purchaser


@pytest.mark.django_db
def test_product_in_cleaned_data(product, form_data):
    form = CreateProductPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["product_id"] == product.pk


@pytest.mark.django_db
def test_quantity_in_cleaned_data(form_data):
    form = CreateProductPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["quantity"] == form_data["quantity"]


@pytest.mark.django_db
def test_save_calls_new_purchase(mock_purchase_model, form_data, purchaser, product):
    form = CreateProductPurchaseForm(form_data)
    form.is_valid()
    form.save()
    mock_purchase_model.objects.new_purchase.assert_called_once_with(
        purchased_by=purchaser, product=product, quantity=form_data["quantity"]
    )


@pytest.mark.django_db
def test_save_sets_purchase_to_instance_attribute(mock_purchase_model, form_data):
    form = CreateProductPurchaseForm(form_data)
    form.is_valid()
    form.save()
    assert form.instance == mock_purchase_model.objects.new_purchase.return_value


@mock.patch("purchases.forms.StockManager")
def test_update_stock_level_calls_get_stock_level(
    mock_stock_manager, purchase, saved_form
):
    mock_stock_manager.get_stock_level.return_value = 50
    saved_form.instance.quantity = 5
    saved_form.update_stock_level()
    mock_stock_manager.get_stock_level.assert_called_once_with(purchase.product)


@mock.patch("purchases.forms.StockManager")
def test_update_stock_level_calls_set_stock_level(
    mock_stock_manager, purchase, saved_form
):
    purchase.quantity = 5
    mock_stock_manager.get_stock_level.return_value = 50
    saved_form.update_stock_level()
    mock_stock_manager.set_stock_level.assert_called_once_with(
        product=purchase.product,
        user=purchase.purchased_by.stcadmin_user,
        new_stock_level=45,
        change_source="Staff purchase by {{ purchase.purchased_by }}",
    )


@mock.patch("purchases.forms.StockManager")
def test_update_stock_level_returns_updated_stock_level(mock_stock_manager, saved_form):
    saved_form.instance.quantity = 5
    mock_stock_manager.get_stock_level.return_value = 50
    returned_value = saved_form.update_stock_level()
    assert returned_value == mock_stock_manager.set_stock_level.return_value


@mock.patch("purchases.forms.StockManager")
@mock.patch("purchases.forms.logging")
def test_update_stock_level_logs_get_stock_level_error(
    mock_logging, mock_stock_manager, saved_form
):
    mock_stock_manager.get_stock_level.side_effect = Exception
    with pytest.raises(Exception):
        saved_form.update_stock_level()
    mock_logging.getLogger.assert_called_once_with("django")
    mock_logging.getLogger.return_value.exception.assert_called_once()


@mock.patch("purchases.forms.StockManager")
@mock.patch("purchases.forms.logging")
def test_update_stock_level_logs_set_stock_level_error(
    mock_logging, mock_stock_manager, saved_form
):
    mock_stock_manager.get_stock_level.return_value = 3
    mock_stock_manager.set_stock_level.side_effect = Exception
    with pytest.raises(Exception):
        saved_form.update_stock_level()
    mock_logging.getLogger.assert_called_once_with("django")
    mock_logging.getLogger.return_value.exception.assert_called_once()


@mock.patch("purchases.forms.StockManager")
@mock.patch("purchases.forms.logging")
def test_update_stock_level_errors_when_stock_level_would_be_set_negative(
    mock_logging, mock_stock_manager, saved_form
):
    saved_form.instance.quantity = 5
    mock_stock_manager.get_stock_level.return_value = 3
    with pytest.raises(Exception):
        saved_form.update_stock_level()
