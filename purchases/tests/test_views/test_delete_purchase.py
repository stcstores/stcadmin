import pytest
from django.urls import reverse

from purchases.models import Purchase


@pytest.fixture
def purchase(purchase_factory):
    return purchase_factory.create(export=None)


@pytest.fixture
def completed_purchase(purchase_factory):
    return purchase_factory.create()


@pytest.fixture
def url(purchase):
    return reverse("purchases:delete_purchase", kwargs={"pk": purchase.pk})


@pytest.fixture
def completed_purchase_url(completed_purchase):
    return reverse("purchases:delete_purchase", kwargs={"pk": completed_purchase.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_response(group_logged_in_client, url):
    return group_logged_in_client.post(url, {})


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/purchase_confirm_delete.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert "form" in get_response.context


@pytest.mark.django_db
def test_contact_is_deleted(purchase, post_response):
    assert Purchase.objects.filter(pk=purchase.pk).exists() is False


@pytest.mark.django_db
def test_success_redirect(purchase, post_response):
    assert post_response.status_code == 302
    assert post_response["location"] == reverse("purchases:manage_purchases")


@pytest.mark.django_db
def test_get_request_for_completed_purchase_returns_404(
    group_logged_in_client, completed_purchase_url
):
    response = group_logged_in_client.get(completed_purchase_url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_post_request_for_completed_purchase_returns_404(
    group_logged_in_client, completed_purchase_url
):
    response = group_logged_in_client.post(completed_purchase_url, {})
    assert response.status_code == 404
