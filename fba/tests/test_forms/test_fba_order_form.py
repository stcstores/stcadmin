import pytest

from fba.forms import FBAOrderForm


@pytest.fixture
def fba_order(fba_order_factory):
    return fba_order_factory.create()


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def region(fba_region_factory):
    return fba_region_factory.create()


@pytest.fixture
def form_data(region, product):
    return {
        "region": region,
        "product_asin": "ntYNHeMhdpbWKp",
        "selling_price": 2182,
        "FBA_fee": 709,
        "aproximate_quantity": 328,
        "is_combinable": False,
        "on_hold": False,
        "is_fragile": False,
        "notes": "Long produce matter.",
        "product": product,
        "product_weight": 2325,
        "product_hs_code": "xUANQwJwUfMUwE",
        "product_purchase_price": "52.49",
        "product_is_multipack": False,
    }


@pytest.mark.django_db
def test_region_queryset_filters_active_without_instance(fba_region_factory):
    region = fba_region_factory.create(active=False)
    assert region not in FBAOrderForm().fields["region"].queryset


@pytest.mark.django_db
def test_region_queryset_does_not_filter_with_instance(fba_order, fba_region_factory):
    region = fba_region_factory.create(active=False)
    assert region in FBAOrderForm(instance=fba_order).fields["region"].queryset


@pytest.mark.django_db
def test_form_submission(form_data):
    form = FBAOrderForm(form_data)
    assert form.is_valid() is True
    form.save()
    assert form.instance.pk
