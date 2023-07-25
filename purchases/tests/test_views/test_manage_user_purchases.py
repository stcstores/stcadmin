import pytest
from django.urls import reverse


@pytest.fixture
def purchaser(staff_factory):
    return staff_factory.create()


@pytest.fixture
def new_purchases(purchase_factory, purchaser):
    return purchase_factory.create_batch(3, purchased_by=purchaser, export=None)


@pytest.fixture
def old_purchase(purchase_factory, purchaser):
    return purchase_factory.create(purchased_by=purchaser)


@pytest.fixture
def other_users_new_purchase(purchase_factory):
    return purchase_factory.create(export=None)


@pytest.fixture
def other_users_old_purchase(purchase_factory):
    return purchase_factory.create()


@pytest.fixture
def url(purchaser):
    return reverse("purchases:manage_user_purchases", kwargs={"staff_pk": purchaser.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/manage_user_purchases.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_purchaser_in_context(get_response, purchaser):
    assert get_response.context["purchaser"] == purchaser


@pytest.mark.django_db
def test_new_purchases_in_purchases(purchaser, new_purchases, get_response):
    for purchase in new_purchases:
        assert purchase in get_response.context["purchases"]


@pytest.mark.django_db
def test_old_purchases_not_in_purchases(old_purchase, get_response):
    assert old_purchase not in get_response.context["purchases"]


@pytest.mark.django_db
def test_other_users_new_purchase_not_in_purchases(
    other_users_new_purchase, get_response
):
    assert other_users_new_purchase not in get_response.context["purchases"]


@pytest.mark.django_db
def test_other_users_old_purchase_not_in_purchases(
    other_users_old_purchase, get_response
):
    assert other_users_old_purchase not in get_response.context["purchases"]
