import pytest
from django.urls import reverse

from purchases.models import BasePurchase


@pytest.fixture
def product_purchase(product_purchase_factory):
    return product_purchase_factory.create(export=None)


@pytest.fixture
def shipping_purchase(shipping_purchase_factory):
    return shipping_purchase_factory.create(export=None)


@pytest.fixture
def other_purchase(other_purchase_factory):
    return other_purchase_factory.create(export=None)


@pytest.fixture
def completed_product_purchase(product_purchase_factory):
    return product_purchase_factory.create()


@pytest.fixture
def url(product_purchase):
    return reverse("purchases:delete_purchase", kwargs={"pk": product_purchase.pk})


@pytest.fixture
def shipping_purchase_url(shipping_purchase):
    return reverse(
        "purchases:delete_purchase",
        kwargs={"pk": shipping_purchase.pk},
    )


@pytest.fixture
def other_purchase_url(other_purchase):
    return reverse(
        "purchases:delete_purchase",
        kwargs={"pk": other_purchase.pk},
    )


@pytest.fixture
def completed_product_purchase_url(completed_product_purchase):
    return reverse(
        "purchases:delete_purchase",
        kwargs={"pk": completed_product_purchase.pk},
    )


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_response(group_logged_in_client, url):
    return group_logged_in_client.post(url, {})


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/purchase_confirm_delete.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert "form" in get_response.context


@pytest.mark.django_db
def test_product_purchase_is_deleted(product_purchase, post_response):
    assert BasePurchase.objects.filter(pk=product_purchase.pk).exists() is False


@pytest.mark.django_db
def test_shipping_purchase_is_deleted(
    shipping_purchase, group_logged_in_client, shipping_purchase_url
):
    response = group_logged_in_client.post(shipping_purchase_url, {})
    assert response.status_code == 302
    assert BasePurchase.objects.filter(pk=shipping_purchase.pk).exists() is False


@pytest.mark.django_db
def test_other_purchase_is_deleted(
    other_purchase, group_logged_in_client, other_purchase_url
):
    response = group_logged_in_client.post(other_purchase_url, {})
    assert response.status_code == 302
    assert BasePurchase.objects.filter(pk=other_purchase.pk).exists() is False


@pytest.mark.django_db
def test_success_redirect(product_purchase, post_response):
    assert post_response.status_code == 302
    assert post_response["location"] == reverse("purchases:manage_purchases")


@pytest.mark.django_db
def test_get_request_for_completed_product_purchase_returns_404(
    group_logged_in_client, completed_product_purchase_url
):
    response = group_logged_in_client.get(completed_product_purchase_url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_post_request_for_completed_product_purchase_returns_404(
    group_logged_in_client, completed_product_purchase_url
):
    response = group_logged_in_client.post(completed_product_purchase_url, {})
    assert response.status_code == 404
