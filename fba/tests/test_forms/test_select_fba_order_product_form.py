import pytest

from fba.forms import SelectFBAOrderProductForm


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def invalid_product(product_factory):
    return product_factory.create(product_range__status="INVALID")


@pytest.mark.django_db
def test_clean_method(product):
    form_data = {"product_SKU": product.sku}
    form = SelectFBAOrderProductForm(form_data)
    assert form.is_valid() is True
    form.clean()
    assert form.cleaned_data["product_SKU"] == product.sku
    assert form.cleaned_data["product"] == product


@pytest.mark.django_db
def test_clean_method_with_invalid_product(invalid_product):
    form_data = {"product_SKU": invalid_product.sku}
    form = SelectFBAOrderProductForm(form_data)
    assert form.is_valid() is False
    assert form.errors["product_SKU"] == ["Product not found"]


@pytest.mark.django_db
def test_clean_method_with_non_existant_product():
    form_data = {"product_SKU": "AAA-BBB-CCC"}
    form = SelectFBAOrderProductForm(form_data)
    assert form.is_valid() is False
    assert form.errors["product_SKU"] == ["Product not found"]
