import pytest
from django.db.models.query import QuerySet

from purchases.forms import ProductSearchForm


@pytest.fixture
def product(product_factory):
    return product_factory.create()


def test_has_search_term_field():
    assert "search_term" in ProductSearchForm().fields


def test_accepts_search_term():
    form = ProductSearchForm({"search_term": "text"})
    assert form.is_valid()


def test_search_term_in_cleaned_data():
    form = ProductSearchForm({"search_term": "text"})
    form.is_valid()
    assert form.cleaned_data["search_term"] == "text"


@pytest.mark.django_db
def test_get_queryset_method_returns_queryset():
    form = ProductSearchForm({"search_term": "text"})
    assert isinstance(form.get_queryset(), QuerySet)


@pytest.mark.django_db
def test_get_queryset_raises_for_invalid_form():
    form = ProductSearchForm()
    with pytest.raises(Exception):
        form.get_queryset()


@pytest.mark.django_db
def test_returns_product_by_sku(product):
    form = ProductSearchForm({"search_term": product.sku})
    assert product in form.get_queryset()


@pytest.mark.django_db
def test_returns_product_by_supplier_sku(product):
    form = ProductSearchForm({"search_term": product.supplier_sku})
    assert product in form.get_queryset()


@pytest.mark.django_db
def test_returns_product_by_barcode(product):
    form = ProductSearchForm({"search_term": product.barcode})
    assert product in form.get_queryset()


@pytest.mark.django_db
def test_returns_product_by_name(product):
    form = ProductSearchForm({"search_term": product.product_range.name})
    assert product in form.get_queryset()


@pytest.mark.django_db
def test_returns_product_by_range_sku(product):
    form = ProductSearchForm({"search_term": product.product_range.sku})
    assert product in form.get_queryset()


@pytest.mark.django_db
def test_does_not_return_unrelated_product(product):
    form = ProductSearchForm({"search_term": "isdjldsfjl"})
    assert product not in form.get_queryset()


@pytest.mark.django_db
def test_does_not_return_archived_product(product_factory):
    product = product_factory.create(is_archived=True)
    form = ProductSearchForm({"search_term": product.sku})
    assert product not in form.get_queryset()
