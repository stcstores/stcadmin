import pytest
from django.urls import reverse
from requests_html import HTML


@pytest.fixture
def path():
    return "home:user"


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
def test_cannot_post(valid_client, url):
    assert valid_client.post(url).status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize(
    "reverse_path,text,count",
    (
        ("home:index", None, 1),
        ("home:change_password", "Change Password", 1),
    ),
)
def test_has_links(reverse_path, text, count, html):
    target = reverse(reverse_path)
    elements = html.find(f'a[href="{target}"]', containing=text)
    assert len(elements) == count


@pytest.mark.django_db
def test_shows_user_groups(get_html, user, group_factory):
    group = group_factory.create()
    user.groups.add(group)
    html = get_html()
    assert html.find("li", containing=group.name)
