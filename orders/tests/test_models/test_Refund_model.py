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
    (models.BreakageRefund, models.LostInPostRefund, models.DemicRefund,),
)
@pytest.mark.django_db
def test_default_contact_contacted(model_class, order):
    refund = model_class(order=order)
    refund.save()
    refund.refresh_from_db()
    assert refund.contact_contacted is False


@pytest.mark.parametrize(
    "model_class",
    (models.BreakageRefund, models.LostInPostRefund, models.DemicRefund,),
)
@pytest.mark.django_db
def test_default_refund_accepted(model_class, order):
    refund = model_class(order=order)
    refund.save()
    refund.refresh_from_db()
    assert refund.refund_accepted is None


@pytest.mark.parametrize(
    "model_class",
    (models.BreakageRefund, models.LostInPostRefund, models.DemicRefund,),
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


@pytest.mark.django_db
def test_from_order(order_factory, product_sale_factory):
    order = order_factory.create()
    products = [
        (product_sale_factory.create(order=order, quantity=3), 2) for _ in range(3)
    ]
    models.Refund.from_order(order, products)
    for product, quantity in products:
        assert models.ProductRefund.objects.filter(
            refund__order=order, product=product, quantity=quantity
        ).exists()


@pytest.mark.django_db
def test_courier_refund_from_order(order_factory, product_sale_factory):
    order = order_factory.create()
    products = [
        (product_sale_factory.create(order=order, quantity=3), 2) for _ in range(3)
    ]
    models.LostInPostRefund.from_order(order, products)
    for product, quantity in products:
        assert models.ProductRefund.objects.filter(
            refund__order=order, product=product, quantity=quantity
        ).exists()
    assert models.Refund.objects.filter(
        order=order,
        CourierRefund___courier=order.shipping_rule.courier_service.courier.courier_type.provider,
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("model", [models.DemicRefund, models.SupplierRefund])
def test_supplier_refund_from_order(
    model, order_factory, product_sale_factory, supplier_factory
):
    order = order_factory.create()
    supplier = supplier_factory.create()
    products = [
        (product_sale_factory.create(order=order, quantity=3, supplier=supplier), 2)
        for _ in range(3)
    ]
    model.from_order(order, products)
    for product, quantity in products:
        assert models.ProductRefund.objects.filter(
            refund__order=order, product=product, quantity=quantity
        ).exists()
    assert models.Refund.objects.filter(
        order=order, SupplierRefund___supplier=products[0][0].supplier,
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("model", [models.DemicRefund, models.SupplierRefund])
def test_supplier_from_order_splits_suppliers(
    model, order_factory, product_sale_factory, supplier_factory
):
    order = order_factory.create()
    products = [
        (product_sale_factory.create(order=order, quantity=3), 2,) for _ in range(3)
    ]
    model.from_order(order, products)
    for product, quantity in products:
        assert models.ProductRefund.objects.filter(
            refund__order=order, product=product, quantity=quantity,
        ).exists()
        assert models.Refund.objects.filter(
            order=order, SupplierRefund___supplier=product.supplier
        ).exists()
    assert models.Refund.objects.filter(order=order).count() == 3
