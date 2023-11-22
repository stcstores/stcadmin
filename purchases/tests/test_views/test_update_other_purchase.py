from decimal import Decimal

import pytest
from django.urls import reverse


@pytest.fixture
def old_quantity():
    return 3


@pytest.fixture
def new_quantity():
    return 5


@pytest.fixture
def old_description():
    return "Old Description"


@pytest.fixture
def new_description():
    return "New Description"


@pytest.fixture
def old_price():
    return 55.80


@pytest.fixture
def new_price():
    return 63.99


@pytest.fixture
def purchase(other_purchase_factory, old_quantity, old_description, old_price):
    return other_purchase_factory.create(
        quantity=old_quantity, description=old_description, price=old_price, export=None
    )


@pytest.fixture
def completed_purchase(other_purchase_factory):
    return other_purchase_factory.create()


@pytest.fixture
def new_purchase_url(purchase):
    return reverse("purchases:update_other_purchase", kwargs={"pk": purchase.id})


@pytest.fixture
def completed_purchase_url(completed_purchase):
    return reverse(
        "purchases:update_other_purchase", kwargs={"pk": completed_purchase.id}
    )


@pytest.fixture
def form_data(new_quantity, new_description, new_price):
    return {
        "quantity": new_quantity,
        "description": new_description,
        "price": new_price,
    }


@pytest.fixture
def get_response(group_logged_in_client, new_purchase_url):
    return group_logged_in_client.get(new_purchase_url)


@pytest.fixture
def post_response(group_logged_in_client, new_purchase_url, form_data):
    return group_logged_in_client.post(new_purchase_url, form_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/update_other_purchase.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_get_initial(old_quantity, old_description, old_price, get_response):
    form = get_response.context["form"]
    assert form.initial == {
        "quantity": old_quantity,
        "description": old_description,
        "price": Decimal(str(old_price)),
    }


@pytest.mark.django_db
def test_post_updates_purchase(
    purchase, new_quantity, new_description, new_price, post_response
):
    purchase.refresh_from_db()
    assert purchase.quantity == new_quantity
    assert purchase.description == new_description
    assert purchase.price == Decimal(str(new_price))


@pytest.mark.django_db
def test_success_url(purchase, post_response):
    assert post_response["location"] == reverse(
        "purchases:manage_user_purchases", kwargs={"staff_pk": purchase.purchased_by.id}
    )


@pytest.mark.django_db
def test_get_request_for_completed_purchase_returns_404(
    group_logged_in_client, completed_purchase_url
):
    response = group_logged_in_client.get(completed_purchase_url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_post_request_for_completed_purchase_returns_404(
    group_logged_in_client, form_data, completed_purchase_url
):
    response = group_logged_in_client.post(completed_purchase_url, form_data)
    assert response.status_code == 404
