import pytest

from fba import models


@pytest.fixture
def fba_order(fba_order_factory):
    return fba_order_factory.create(status_fulfilled=True)


@pytest.fixture
def tracking_number(fba_order, fba_tracking_number_factory):
    return fba_tracking_number_factory.create(fba_order=fba_order)


@pytest.mark.django_db
def test_full_clean(tracking_number):
    assert tracking_number.full_clean() is None


@pytest.mark.django_db
def test_has_fba_order_attribute(tracking_number):
    assert isinstance(tracking_number.fba_order, models.FBAOrder)


@pytest.mark.django_db
def test_has_tracking_number_attribute(tracking_number):
    assert isinstance(tracking_number.tracking_number, str)


@pytest.mark.django_db
def test_str_method(tracking_number):
    assert str(tracking_number) == tracking_number.tracking_number


@pytest.mark.django_db
def test_update_tracking_numbers_deletes_old_tracking_numbers(
    fba_order, fba_tracking_number_factory
):
    old_tracking_number = fba_tracking_number_factory.create(
        fba_order=fba_order, tracking_number="TRK_9988"
    )
    models.FBATrackingNumber.objects.update_tracking_numbers(fba_order, "TRK_8899")
    with pytest.raises(models.FBATrackingNumber.DoesNotExist):
        old_tracking_number.refresh_from_db()


@pytest.mark.django_db
def test_update_tracking_numbers_adds_new_tracking_numbers(
    fba_order, fba_tracking_number_factory
):
    tracking_numbers = ["TK8899", "TK8900", "TK8901"]
    models.FBATrackingNumber.objects.update_tracking_numbers(
        fba_order, *tracking_numbers
    )
    models.FBATrackingNumber.objects.filter(fba_order=fba_order).values_list(
        "tracking_number", flat=True
    ) == tracking_numbers


@pytest.mark.django_db
def test_update_tracking_numbers_leaves_existing_tracking_numbers(
    fba_order, fba_tracking_number_factory
):
    old_tracking_number = fba_tracking_number_factory.create(
        fba_order=fba_order, tracking_number="TRK_9988"
    )
    models.FBATrackingNumber.objects.update_tracking_numbers(
        fba_order, "TRK_9988", "TRK_8899"
    )
    old_tracking_number.refresh_from_db()
