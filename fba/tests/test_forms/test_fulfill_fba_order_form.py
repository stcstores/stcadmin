import pytest

from fba.forms import FulfillFBAOrderForm


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_printed=True)


@pytest.fixture
def fulfilled_order(fba_order_factory):
    return fba_order_factory.create(status_fulfilled=True)


@pytest.fixture
def hidden_packer(staff_factory):
    return staff_factory.create(fba_packer=True, hidden=True)


@pytest.mark.django_db
def test_sets_box_weight_label(order):
    form = FulfillFBAOrderForm(instance=order)
    assert form.fields["box_weight"].label == "Box weight (kg)"


@pytest.mark.django_db
def test_sets_box_weight_max(order):
    form = FulfillFBAOrderForm(instance=order)
    assert form.fields["box_weight"].widget.attrs["max"] == order.region.max_weight


@pytest.mark.django_db
def test_sets_box_weight_required(order):
    form = FulfillFBAOrderForm(instance=order)
    assert form.fields["box_weight"].required is True


@pytest.mark.django_db
def test_sets_quantity_sent_required(order):
    form = FulfillFBAOrderForm(instance=order)
    assert form.fields["quantity_sent"].required is True


@pytest.mark.django_db
def test_sets_fulfilled_by_required(order):
    form = FulfillFBAOrderForm(instance=order)
    assert form.fields["fulfilled_by"].required is True


@pytest.mark.django_db
def test_filters_fulfilled_by_when_field_is_empty(order, hidden_packer):
    form = FulfillFBAOrderForm(instance=order)
    assert form.fields["fulfilled_by"].queryset.contains(hidden_packer) is False


@pytest.mark.django_db
def test_does_not_filter_fulfilled_by_when_field_is_not_empty(
    fulfilled_order, hidden_packer
):
    form = FulfillFBAOrderForm(instance=fulfilled_order)
    assert form.fields["fulfilled_by"].queryset.contains(hidden_packer)


@pytest.fixture
def fba_packer(staff_factory):
    return staff_factory.create(fba_packer=True)


@pytest.fixture
def form_data(fba_packer):
    return {
        "box_weight": 12,
        "quantity_sent": 50,
        "fulfilled_by": fba_packer,
        "update_stock_level_when_complete": False,
        "notes": "Some Text",
    }


@pytest.mark.django_db
def test_form_submission(order, form_data):
    form = FulfillFBAOrderForm(form_data, instance=order)
    assert form.is_valid()
    form.save()
    order.refresh_from_db()
    assert order.box_weight == form_data["box_weight"]
    assert order.quantity_sent == form_data["quantity_sent"]
    assert order.fulfilled_by == form_data["fulfilled_by"]
    assert (
        order.update_stock_level_when_complete
        == form_data["update_stock_level_when_complete"]
    )
    assert order.notes == form_data["notes"]
