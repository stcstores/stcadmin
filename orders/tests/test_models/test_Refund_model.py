import pytest

from orders import models


@pytest.fixture
def order(order_factory):
    return order_factory.create()


@pytest.fixture
def notes():
    return "Some notes on the refund."


@pytest.mark.parametrize(
    "model_class",
    (
        models.BreakageRefund,
        models.PackingMistakeRefund,
        models.LinkingMistakeRefund,
        models.LostInPostRefund,
        models.DemicRefund,
    ),
)
@pytest.mark.django_db
def test_order_set(model_class, order):
    refund = model_class(order=order)
    refund.save()
    refund.refresh_from_db()
    assert refund.order == order


@pytest.mark.parametrize(
    "model_class",
    (
        models.BreakageRefund,
        models.PackingMistakeRefund,
        models.LinkingMistakeRefund,
        models.LostInPostRefund,
        models.DemicRefund,
    ),
)
@pytest.mark.django_db
def test_default_contact_contacted(model_class, order):
    refund = model_class(order=order)
    refund.save()
    refund.refresh_from_db()
    assert refund.contact_contacted is False


@pytest.mark.parametrize(
    "model_class",
    (
        models.BreakageRefund,
        models.PackingMistakeRefund,
        models.LinkingMistakeRefund,
        models.LostInPostRefund,
        models.DemicRefund,
    ),
)
@pytest.mark.django_db
def test_default_refund_accepted(model_class, order):
    refund = model_class(order=order)
    refund.save()
    refund.refresh_from_db()
    assert refund.refund_accepted is None


@pytest.mark.parametrize(
    "model_class",
    (
        models.BreakageRefund,
        models.PackingMistakeRefund,
        models.LinkingMistakeRefund,
        models.LostInPostRefund,
        models.DemicRefund,
    ),
)
@pytest.mark.django_db
def test_default_refund_amount(model_class, order):
    refund = model_class(order=order)
    refund.save()
    refund.refresh_from_db()
    assert refund.refund_amount is None


@pytest.mark.parametrize(
    "model_class",
    (
        models.BreakageRefund,
        models.PackingMistakeRefund,
        models.LinkingMistakeRefund,
        models.LostInPostRefund,
        models.DemicRefund,
    ),
)
@pytest.mark.django_db
def test_default_closed(model_class, order):
    refund = model_class(order=order)
    refund.save()
    refund.refresh_from_db()
    assert refund.closed is False


@pytest.mark.parametrize(
    "model_class",
    (
        models.BreakageRefund,
        models.PackingMistakeRefund,
        models.LinkingMistakeRefund,
        models.LostInPostRefund,
        models.DemicRefund,
    ),
)
@pytest.mark.django_db
def test_get_absolute_url_method(model_class, order):
    refund = model_class(order=order)
    refund.save()
    refund.refresh_from_db()
    assert refund.get_absolute_url() == f"/orders/refund/{refund.id}/"


@pytest.mark.parametrize(
    "model_class",
    (
        models.BreakageRefund,
        models.PackingMistakeRefund,
        models.LinkingMistakeRefund,
        models.LostInPostRefund,
        models.DemicRefund,
    ),
)
@pytest.mark.django_db
def test_default_notes(model_class, order):
    refund = model_class(order=order)
    refund.save()
    refund.refresh_from_db()
    assert refund.notes == ""


@pytest.mark.parametrize(
    "model_class",
    (
        models.BreakageRefund,
        models.PackingMistakeRefund,
        models.LinkingMistakeRefund,
        models.LostInPostRefund,
        models.DemicRefund,
    ),
)
@pytest.mark.django_db
def test_default_can_set_notes(model_class, order, notes):
    refund = model_class(order=order, notes=notes)
    refund.save()
    refund.refresh_from_db()
    assert refund.notes == notes


@pytest.mark.parametrize(
    "model_class,expected",
    (
        (models.BreakageRefund, "Breakage"),
        (models.PackingMistakeRefund, "Packing Mistake"),
        (models.LinkingMistakeRefund, "Linking Mistake"),
        (models.LostInPostRefund, "Lost In Post"),
        (models.DemicRefund, "Demic"),
    ),
)
@pytest.mark.django_db
def test_reason_method(model_class, expected, order):
    refund = model_class(order=order)
    assert refund.reason() == expected
