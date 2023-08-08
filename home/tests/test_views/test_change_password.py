import pytest
from django.urls import reverse
from requests_html import HTML


@pytest.fixture
def path():
    return "home:change_password"


@pytest.fixture
def url(path):
    return reverse(path)


@pytest.fixture
def get_page_text(valid_client, url):
    def _get_page_text():
        response = valid_client.get(url)
        return response.content.decode("utf8")

    return _get_page_text


@pytest.fixture
def page_text(get_page_text):
    return get_page_text()


@pytest.fixture
def html(page_text):
    return HTML(html=page_text)


@pytest.fixture
def get_html(get_page_text):
    def _get_html():
        return HTML(html=get_page_text())

    return _get_html


@pytest.mark.django_db
def test_cannot_access_logged_out(logged_out_client, url):
    assert logged_out_client.get(url).status_code == 302


@pytest.mark.django_db
def test_can_post(valid_client, url):
    assert valid_client.post(url).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "reverse_path,count",
    (("home:index", 1),),
)
def test_has_links(reverse_path, count, html):
    target = reverse(reverse_path)
    elements = html.find(f'a[href="{target}"]')
    assert len(elements) == count


@pytest.mark.django_db
def test_contains_form(html):
    assert html.find('form[method="post"]')


@pytest.mark.django_db
def test_contains_old_password_input(html):
    assert html.find('input[name="old_password"][type="password"]')


@pytest.mark.django_db
def test_contains_new_password_input(html):
    assert html.find('input[name="new_password1"][type="password"]')


@pytest.mark.django_db
def test_contains_new_password_confirmation_input(html):
    assert html.find('input[name="new_password2"][type="password"]')


@pytest.fixture
def new_password():
    return "lsndfoisdnsdoi"


@pytest.mark.django_db
def test_changes_password(user, url, valid_client, new_password, test_password):
    valid_client.post(
        url,
        {
            "old_password": test_password,
            "new_password1": new_password,
            "new_password2": new_password,
        },
    )
    user.refresh_from_db()
    assert user.check_password("Password") is False
    assert user.check_password(new_password)


@pytest.mark.django_db
def test_redirects(user, url, test_password, valid_client, new_password):
    response = valid_client.post(
        url,
        {
            "old_password": test_password,
            "new_password1": new_password,
            "new_password2": new_password,
        },
    )
    assert response.status_code == 302
    assert response["Location"] == reverse("password_change_done")


@pytest.mark.django_db
def test_uses_template(valid_client, url):
    response = valid_client.get(url)
    assert "home/change_password.html" in (t.name for t in response.templates)
