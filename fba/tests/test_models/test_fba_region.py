import pytest

from fba import models
from shipping.models import Country, Currency


@pytest.fixture
def fba_region(fba_region_factory):
    return fba_region_factory.create()


@pytest.mark.django_db
def test_full_clean(fba_region):
    assert fba_region.full_clean() is None


@pytest.mark.django_db
def test_has_name_attribute(fba_region):
    assert isinstance(fba_region.name, str)


@pytest.mark.django_db
def test_has_country_attribute(fba_region):
    assert isinstance(fba_region.country, Country)


@pytest.mark.django_db
def test_has_postage_price_attribute(fba_region):
    assert isinstance(fba_region.postage_price, int)


@pytest.mark.django_db
def test_has_postage_per_kg_attribute(fba_region):
    assert isinstance(fba_region.postage_per_kg, int)


@pytest.mark.django_db
def test_has_postage_overhead_g_attribute(fba_region):
    assert isinstance(fba_region.postage_overhead_g, int)


@pytest.mark.django_db
def test_has_min_shipping_cost_attribute(fba_region):
    assert isinstance(fba_region.min_shipping_cost, int)


@pytest.mark.django_db
def test_has_max_weight_attribute(fba_region):
    assert isinstance(fba_region.max_weight, int)


@pytest.mark.django_db
def test_has_max_size_attribute(fba_region):
    assert isinstance(fba_region.max_size, float)


@pytest.mark.django_db
def test_has_fulfillment_unit_attribute(fba_region):
    assert fba_region.fulfillment_unit in (
        models.FBARegion.METRIC,
        models.FBARegion.IMPERIAL,
    )


@pytest.mark.django_db
def test_has_auto_close_attribute(fba_region):
    assert isinstance(fba_region.auto_close, bool)


@pytest.mark.django_db
def test_has_curency_attribute(fba_region):
    assert isinstance(fba_region.currency, Currency)


@pytest.mark.django_db
def test_has_warehouse_required_attribute(fba_region):
    assert fba_region.warehouse_required is False


@pytest.mark.django_db
def test_has_expiry_date_required_attribute(fba_region):
    assert fba_region.expiry_date_required is False


@pytest.mark.django_db
def test_has_position_attribute(fba_region):
    assert fba_region.position == 9999


@pytest.mark.django_db
def test_has_active_attribute(fba_region):
    assert fba_region.active is True


# Test Methods


@pytest.mark.django_db
def test_str_method(fba_region):
    assert str(fba_region) == fba_region.name


@pytest.mark.django_db
def test_flag_method(fba_region):
    assert isinstance(fba_region.flag(), str)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "unit,expected",
    ((models.FBARegion.METRIC, "cm"), (models.FBARegion.IMPERIAL, "inches")),
)
def test_size_unit_method(unit, expected, fba_region_factory):
    region = fba_region_factory.create(fulfillment_unit=unit)
    assert region.size_unit() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "unit,expected",
    ((models.FBARegion.METRIC, "kg"), (models.FBARegion.IMPERIAL, "lb")),
)
def test_weight_unit_method(unit, expected, fba_region_factory):
    region = fba_region_factory.create(fulfillment_unit=unit)
    assert region.weight_unit() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "unit,expected",
    ((models.FBARegion.METRIC, "5 kg"), (models.FBARegion.IMPERIAL, "11 lb")),
)
def test_max_weight_local_method(unit, expected, fba_region_factory):
    region = fba_region_factory.create(max_weight=5, fulfillment_unit=unit)
    assert region.max_weight_local() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "unit,expected",
    ((models.FBARegion.METRIC, "5 cm"), (models.FBARegion.IMPERIAL, "5 inches")),
)
def test_max_size_local_method(unit, expected, fba_region_factory):
    region = fba_region_factory.create(max_size=5, fulfillment_unit=unit)
    assert region.max_size_local() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "weight,postage_price,postage_overhead,min_shipping_cost,postage_per_kg,expected",
    (
        (5400, 9500, 6200, 2400, 2, 9500),
        (5400, None, 6200, 50200, 2, 50200),
        (5400, None, 6200, 1, 2, 23),
    ),
)
def test_calculate_shipping(
    weight,
    postage_price,
    postage_overhead,
    min_shipping_cost,
    postage_per_kg,
    expected,
    fba_region_factory,
):
    region = fba_region_factory.create(
        postage_price=postage_price,
        postage_overhead_g=postage_overhead,
        min_shipping_cost=min_shipping_cost,
        postage_per_kg=postage_per_kg,
    )
    assert region.calculate_shipping(weight) == expected
