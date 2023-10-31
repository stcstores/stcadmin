import datetime as dt

import pytest
from django import forms

from fba.forms import StopFBAOrderForm


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True)


@pytest.fixture
def form_data():
    return {
        "is_stopped": True,
        "stopped_at": dt.datetime(2023, 2, 2),
        "stopped_until": dt.datetime(2023, 3, 3),
        "stopped_reason": "B",
    }


def test_is_stopped_field_widget():
    form = StopFBAOrderForm()
    assert isinstance(form.fields["is_stopped"].widget, forms.HiddenInput)


def test_stopped_at_field_widget():
    form = StopFBAOrderForm()
    assert isinstance(form.fields["stopped_at"].widget, forms.HiddenInput)


def test_stopped_until_field_widget():
    form = StopFBAOrderForm()
    assert isinstance(form.fields["stopped_until"].widget, forms.DateInput)


def test_fields():
    form = StopFBAOrderForm()
    assert sorted(list(form.fields.keys())) == [
        "is_stopped",
        "stopped_at",
        "stopped_reason",
        "stopped_until",
    ]


@pytest.mark.django_db
def test_update_with_form(order, form_data):
    form = StopFBAOrderForm(form_data, instance=order)
    assert form.is_valid() is True
    form.save()
    order.refresh_from_db()
    order.is_stopped = True
    order.stopped_at = form_data["stopped_at"]
    order.stopped_reason = form_data["stopped_at"]
    order.stopped_until = form_data["stopped_until"]
