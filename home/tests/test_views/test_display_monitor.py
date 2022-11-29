import pytest
from django.urls import reverse
from requests_html import HTML


@pytest.fixture
def path():
    return "home:monitor"


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


@pytest.mark.django_db
def test_can_access_logged_out(logged_out_client, url):
    assert logged_out_client.get(url).status_code == 200


@pytest.mark.django_db
def test_cannot_post(valid_client, url):
    assert valid_client.post(url).status_code == 405


@pytest.mark.django_db
def test_contains_buttons(html):
    assert html.find('div[class="buttons"]')


@pytest.mark.django_db
def test_contains_display(html):
    assert html.find('div[class="display"]')


@pytest.mark.django_db
@pytest.mark.parametrize(
    "reverse_path",
    ("orders:pack_count_monitor", "feedback:monitor", "orders:undispatched_data"),
)
def test_containts_monitor_page_urls(reverse_path, page_text):
    assert reverse(reverse_path) in page_text
