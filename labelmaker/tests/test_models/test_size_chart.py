import pytest

from inventory.models import Supplier
from labelmaker import models


@pytest.fixture
def size_chart(size_chart_factory):
    size_chart = size_chart_factory.create()
    size_chart.full_clean()
    return size_chart


@pytest.fixture
def new_size_chart():
    size_chart = models.SizeChart(name="New Size Chart")
    size_chart.full_clean()
    return size_chart


@pytest.mark.django_db
def test_size_chart_has_supplier_attribute(size_chart):
    assert isinstance(size_chart.supplier, Supplier)


@pytest.mark.django_db
def test_supplier_defaults_to_none(new_size_chart):
    assert new_size_chart.supplier is None


@pytest.mark.django_db
def test_size_chart_has_name_attribute(size_chart):
    assert isinstance(size_chart.name, str)
    assert len(size_chart.name) > 0


@pytest.mark.django_db
def test_by_supplier_method(size_chart_factory):
    size_chart_1 = size_chart_factory.create()
    size_chart_2 = size_chart_factory.create()
    size_chart_3 = size_chart_factory.create()
    size_chart_4 = size_chart_factory.create(supplier=size_chart_1.supplier)
    size_chart_5 = size_chart_factory.create(supplier=None)
    returned_value = models.SizeChart.by_supplier()
    assert set(returned_value.keys()) == {
        size_chart_1.supplier,
        size_chart_2.supplier,
        size_chart_3.supplier,
        None,
    }
    assert set(returned_value[size_chart_1.supplier]) == {size_chart_1, size_chart_4}
    assert returned_value[size_chart_2.supplier] == [size_chart_2]
    assert returned_value[size_chart_3.supplier] == [size_chart_3]
    assert returned_value[None] == [size_chart_5]


@pytest.mark.django_db
def test_get_absolute_url_method(size_chart):
    expected = f"/labelmaker/product_labels/update_size_chart/{size_chart.id}/"
    assert size_chart.get_absolute_url() == expected


@pytest.mark.django_db
def test_get_delete_url_method(size_chart):
    expected = f"/labelmaker/product_labels/delete_size_chart/{size_chart.id}/"
    assert size_chart.get_delete_url() == expected


@pytest.mark.django_db
def test_get_edit_sizes_url_method(size_chart):
    expected = f"/labelmaker/product_labels/edit_size_chart_sizes/{size_chart.id}/"
    assert size_chart.get_edit_sizes_url() == expected


@pytest.mark.django_db
def test_get_use_url_method(size_chart):
    expected = f"/labelmaker/product_labels/create_product_labels/{size_chart.id}/"
    assert size_chart.get_use_url() == expected


@pytest.mark.django_db
def test_str_method_with_supplier(size_chart_factory):
    size_chart = size_chart_factory.create(
        name="Ladies Clothing", supplier__name="Baum Trading"
    )
    assert str(size_chart) == "Baum Trading - Ladies Clothing"


@pytest.mark.django_db
def test_str_method_without_supplier(size_chart_factory):
    size_chart = size_chart_factory.create(supplier=None)
    assert str(size_chart) == size_chart.name
