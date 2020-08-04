import pytest
from django.shortcuts import reverse
from pytest_django.asserts import assertTemplateUsed

from orders import forms, models


@pytest.fixture
def order(db, order_factory, product_sale_factory):
    order = order_factory.create()
    return order


@pytest.fixture
def url():
    def _url(refund_type, order):
        return f"/orders/refund/select_products/{refund_type}/{order.id}/"

    return _url


@pytest.fixture
def valid_get_response(valid_get_request, url, order):
    return valid_get_request(url("broken", order))


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url).content.decode("utf8")


@pytest.fixture
def products(order, product_sale_factory):
    return [product_sale_factory.create(order=order, quantity=2) for _ in range(3)]


@pytest.fixture
def form_data(products):
    form_data = {
        "form-TOTAL_FORMS": len(products),
        "form-INITIAL_FORMS": len(products),
        "form-MAX_NUM_FORMS": len(products),
    }
    for i, product in enumerate(products):
        form_data[f"form-{i}-product_sale_id"] = product.id
        form_data[f"form-{i}-quantity"] = 1
    return form_data


def test_logged_in_get(url, order, logged_in_client):
    response = logged_in_client.get(url("broken", order))
    assert response.status_code == 403


def test_logged_out_get(client, url, order):
    response = client.get(url("broken", order))
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url, order):
    response = group_logged_in_client.get(url("broken", order))
    assert response.status_code == 200


def test_logged_in_post(url, order, logged_in_client, form_data):
    response = logged_in_client.post(url("broken", order), form_data)
    assert response.status_code == 403


def test_logged_out_post(client, url, order, form_data):
    response = client.post(url("broken", order), form_data)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url, order, form_data):
    response = group_logged_in_client.post(url("broken", order), form_data)
    assert response.status_code == 302


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "orders/refunds/product_form.html")
        is not False
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "refund_type,refund_class",
    (
        (forms.CreateRefund.BROKEN, models.BreakageRefund),
        (forms.CreateRefund.PACKING_MISTAKE, models.PackingMistakeRefund),
        (forms.CreateRefund.LINKING_MISTAKE, models.LinkingMistakeRefund),
        (forms.CreateRefund.LOST_IN_POST, models.LostInPostRefund),
        (forms.CreateRefund.DEMIC, models.DemicRefund),
    ),
)
def test_creates_refund(
    refund_type, refund_class, group_logged_in_client, url, order, form_data
):
    group_logged_in_client.post(url(refund_type, order), form_data)
    assert refund_class.objects.filter(order=order).exists()


@pytest.mark.django_db
def test_refund_products_created(
    group_logged_in_client, url, order, form_data, products
):
    group_logged_in_client.post(url("broken", order), form_data)
    for product in products:
        assert models.ProductRefund.objects.filter(
            refund__order=order, product=product, quantity=1
        ).exists()


@pytest.mark.django_db
def test_redirects(group_logged_in_client, url, order, form_data):
    response = group_logged_in_client.post(url("broken", order), form_data)
    assert response.url == reverse("orders:refund_list") + f"?order_ID={order.order_ID}"


@pytest.mark.django_db
def test_redirects_to_refund_when_only_one_created(
    group_logged_in_client, url, order, form_data
):
    form_data["form-1-quantity"] = 0
    form_data["form-2-quantity"] = 0
    response = group_logged_in_client.post(url("broken", order), form_data)
    assert response.url == models.Refund.objects.get(order=order).get_absolute_url()


@pytest.mark.django_db
def test_does_not_create_product_when_quantity_is_zero(
    group_logged_in_client, url, order, form_data, products
):
    form_data["form-0-quantity"] = 0
    group_logged_in_client.post(url("broken", order), form_data)
    assert models.ProductRefund.objects.filter(product=products[0]).exists() is False


def test_a_refund_is_created_for_each_supplier(
    order, url, group_logged_in_client, form_data, products, supplier_factory
):
    for product in products:
        product.supplier = supplier_factory.create()
        product.save()
    group_logged_in_client.post(url("broken", order), form_data)
    assert models.Refund.objects.filter(order=order).count() == len(products)
