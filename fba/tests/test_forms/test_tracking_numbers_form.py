import json

import pytest

from fba import models
from fba.forms import TrackingNumbersForm


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create()


@pytest.fixture
def tracking_numbers():
    return ["AAA", "BBB", "CCC"]


@pytest.fixture
def tracking_numbers_json(tracking_numbers):
    return json.dumps(tracking_numbers)


@pytest.mark.django_db
def test_clean_tracking_numbers(order, tracking_numbers, tracking_numbers_json):
    form = TrackingNumbersForm(
        {"tracking_numbers": tracking_numbers_json}, instance=order
    )
    assert form.is_valid() is True
    assert form.cleaned_data["tracking_numbers"] == tracking_numbers


@pytest.mark.django_db
def test_updates_tracking_numbers(order, tracking_numbers, tracking_numbers_json):
    form = TrackingNumbersForm(
        {"tracking_numbers": tracking_numbers_json}, instance=order
    )
    assert form.is_valid() is True
    form.save()
    for tracking_number in tracking_numbers:
        assert models.FBATrackingNumber.objects.filter(
            fba_order=order, tracking_number=tracking_number
        ).exists()
    assert order.closed_at is not None


@pytest.mark.django_db
def test_does_not_close_order_without_tracking_numbers(order):
    form = TrackingNumbersForm({"tracking_numbers": "[]"}, instance=order)
    assert form.is_valid() is True
    form.save()
    assert models.FBATrackingNumber.objects.filter(fba_order=order).exists() is False
    assert order.closed_at is None
