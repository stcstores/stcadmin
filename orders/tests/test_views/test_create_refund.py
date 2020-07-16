import pytest
from django.shortcuts import reverse
from pytest_django.asserts import assertTemplateUsed

from orders import forms, models


@pytest.fixture
def url():
    return "/orders/create_refund/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url).content.decode("utf8")


@pytest.fixture
def order(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order)
    return order


@pytest.fixture
def form_data(order):
    return {"order_ID": order.order_ID, "refund_type": forms.CreateRefund.BROKEN}


def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url, form_data):
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 302


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(
            valid_get_response, "orders/refunds/create_refund_order_select.html"
        )
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
    form_data["refund_type"] = refund_type
    group_logged_in_client.post(url, form_data)
    assert refund_class.objects.filter(order=order).exists()


@pytest.mark.django_db
def test_creates_product_refund(order, group_logged_in_client, url, form_data):
    group_logged_in_client.post(url, form_data)
    assert models.ProductRefund.objects.filter(
        refund__order=order, product=order.productsale_set.first()
    ).exists()


@pytest.mark.django_db
def test_redirects_if_order_has_multiple_products(
    order, product_sale_factory, group_logged_in_client, url, form_data
):
    product_sale_factory.create(order=order)
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 302
    assert response.url == reverse(
        "orders:select_refund_products", args=[form_data["refund_type"], order.pk]
    )


@pytest.mark.django_db
def test_redirects_if_order_has_multiple_of_a_product(
    order, product_sale_factory, group_logged_in_client, url, form_data
):
    order.productsale_set.update(quantity=2)
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 302
    assert response.url == reverse(
        "orders:select_refund_products", args=[form_data["refund_type"], order.pk]
    )


@pytest.mark.django_db
def test_invalid_order_ID(order, group_logged_in_client, url, form_data):
    form_data["order_ID"] = "9999999999"
    response = group_logged_in_client.post(url, form_data)
    assert "Order not found" in response.content.decode("utf8")
