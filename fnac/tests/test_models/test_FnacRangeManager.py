import pytest

from fnac import models


@pytest.fixture
def range_with_category(fnac_range_factory, category_factory):
    return fnac_range_factory.create(category=category_factory.create())


@pytest.fixture
def range_without_category(fnac_range_factory):
    return fnac_range_factory.create(category=None)


@pytest.mark.django_db
def test_has_category_returns_when_product_has_category(
    range_with_category, range_without_category
):
    assert range_with_category in models.FnacRange.objects.has_category()


@pytest.mark.django_db
def test_has_category_does_not_return_when_product_has_no_category(
    range_with_category, range_without_category
):
    assert range_without_category not in models.FnacRange.objects.has_category()


@pytest.mark.django_db
def test_missing_category_returns_when_product_has_no_category(
    range_with_category, range_without_category
):
    assert range_without_category in models.FnacRange.objects.missing_category()


@pytest.mark.django_db
def test_missing_category_does_not_return_when_product_has_category(
    range_with_category, range_without_category
):
    assert range_with_category not in models.FnacRange.objects.missing_category()
