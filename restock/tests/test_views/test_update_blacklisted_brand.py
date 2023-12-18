import pytest
from django.urls import reverse


@pytest.fixture
def blacklisted_brand(blacklisted_brand_factory):
    return blacklisted_brand_factory.create()


@pytest.fixture
def url(blacklisted_brand):
    return reverse(
        "restock:update_blacklisted_brand", kwargs={"pk": blacklisted_brand.pk}
    )


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_data(blacklisted_brand):
    return {
        "name": blacklisted_brand.name,
        "comment": blacklisted_brand.comment,
    }


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/blacklistedbrand_form.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert "form" in get_response.context


@pytest.mark.django_db
def test_updates_name(group_logged_in_client, url, post_data, blacklisted_brand):
    post_data["name"] == "Updated Brand Name"
    group_logged_in_client.post(url, post_data)
    blacklisted_brand.refresh_from_db()
    assert blacklisted_brand.name == post_data["name"]


@pytest.mark.django_db
def test_updates_comment(group_logged_in_client, url, post_data, blacklisted_brand):
    post_data["comment"] == "Updated Brand comment"
    group_logged_in_client.post(url, post_data)
    blacklisted_brand.refresh_from_db()
    assert blacklisted_brand.name == post_data["name"]


@pytest.mark.django_db
def test_success_redirect(post_data, group_logged_in_client, url):
    response = group_logged_in_client.post(url, post_data)
    assert response.status_code == 302
    assert response["location"] == reverse("restock:brand_blacklist")
