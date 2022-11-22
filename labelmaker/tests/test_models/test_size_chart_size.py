import pytest

from labelmaker import models


@pytest.fixture
def size_chart_size(size_chart_size_factory):
    size_chart_size = size_chart_size_factory.create()
    size_chart_size.full_clean()
    return size_chart_size


@pytest.fixture
def new_size_chart_size(size_chart_factory):
    new_size_chart_size = models.SizeChartSize(
        size_chart=size_chart_factory.create(),
        uk_size="5",
        us_size="6",
        eu_size="7",
        au_size="8",
    )
    return new_size_chart_size


@pytest.mark.django_db
def test_has_size_chart_attribute(size_chart_size):
    assert isinstance(size_chart_size.size_chart, models.SizeChart)


@pytest.mark.django_db
def test_has_sort_attribute(size_chart_size):
    assert isinstance(size_chart_size.sort, int)


@pytest.mark.django_db
def test_sort_attribute_defaults_to_zero(new_size_chart_size):
    assert new_size_chart_size.sort == 0


@pytest.mark.django_db
def test_has_name_attribute(size_chart_size):
    assert isinstance(size_chart_size.name, str)
    assert len(size_chart_size.name) > 0


@pytest.mark.django_db
def test_name_defaults_to_none(new_size_chart_size):
    assert new_size_chart_size.name is None


@pytest.mark.django_db
def test_has_uk_size_attribute(size_chart_size):
    assert isinstance(size_chart_size.uk_size, str)
    assert len(size_chart_size.uk_size) > 0


@pytest.mark.django_db
def test_has_eu_size_attribute(size_chart_size):
    assert isinstance(size_chart_size.eu_size, str)
    assert len(size_chart_size.eu_size) > 0


@pytest.mark.django_db
def test_has_us_size_attribute(size_chart_size):
    assert isinstance(size_chart_size.us_size, str)
    assert len(size_chart_size.us_size) > 0


@pytest.mark.django_db
def test_has_au_size_attribute(size_chart_size):
    assert isinstance(size_chart_size.au_size, str)
    assert len(size_chart_size.au_size) > 0


@pytest.mark.django_db
def test_str_method(size_chart_size_factory):
    size_chart_size = size_chart_size_factory.create(
        size_chart__name="Shoes", uk_size="5"
    )
    assert str(size_chart_size) == "Shoes - UK 5"


@pytest.mark.django_db
def test_get_sizes_method(size_chart_size_factory):
    size_chart_size = size_chart_size_factory.create(
        uk_size="5", us_size="6", eu_size="7", au_size="8"
    )
    assert size_chart_size.get_sizes() == (
        ("UK", "5"),
        ("EUR", "7"),
        ("USA", "6"),
        ("AUS", "8"),
    )
