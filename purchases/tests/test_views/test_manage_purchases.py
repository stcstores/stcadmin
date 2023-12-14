import pytest
from django.urls import reverse


@pytest.fixture
def staff(staff_factory):
    return staff_factory.create_batch(3)


@pytest.fixture
def staff_with_no_purchase(staff_factory, product_purchase_factory):
    staff_member = staff_factory.create()
    product_purchase_factory.create(purchased_by=staff_member)
    return staff_member


@pytest.fixture
def purchases(staff, product_purchase_factory):
    purchases = []
    for staff_member in staff:
        purchases.append(
            product_purchase_factory.create_batch(
                3, purchased_by=staff_member, export=None
            )
        )
    return purchases


@pytest.fixture
def url():
    return reverse("purchases:manage_purchases")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/manage_purchases.html" in [t.name for t in get_response.templates]


@pytest.mark.django_db
def test_purchasers_in_purchasers(
    staff, purchases, staff_with_no_purchase, get_response
):
    for staff_member in staff:
        assert staff_member in get_response.context["purchasers"]


@pytest.mark.django_db
def test_staff_members_without_purchase_are_not_in_purchasers(
    staff, staff_with_no_purchase, get_response
):
    assert staff_with_no_purchase not in get_response.context["purchasers"]
