import pytest
from django.urls import reverse


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def url(supplier):
    return reverse("inventory:toggle_supplier_active", kwargs={"pk": supplier.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_active_supplier_is_set_inactive(supplier, group_logged_in_client, url):
    supplier.active = True
    supplier.save()
    group_logged_in_client.get(url)
    supplier.refresh_from_db()
    assert supplier.active is False


@pytest.mark.django_db
def test_inactive_supplier_is_set_active(supplier, group_logged_in_client, url):
    supplier.active = False
    supplier.save()
    group_logged_in_client.get(url)
    supplier.refresh_from_db()
    assert supplier.active is True


@pytest.mark.django_db
def test_success_redirect(get_response, supplier):
    assert get_response.status_code == 302
    assert get_response["location"] == supplier.get_absolute_url()
