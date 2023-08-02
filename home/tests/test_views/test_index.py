import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from requests_html import HTML


@pytest.fixture
def path():
    return "home:index"


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
    (("home:index", "Home", 1),),
)
def test_has_links(reverse_path, text, count, html):
    target = reverse(reverse_path)
    elements = html.find(f'a[href="{target}"]', containing=text)
    assert len(elements) == count


@pytest.mark.django_db
def test_links_to_external_links(get_html, external_link_factory):
    external_link = external_link_factory.create()
    html = get_html()
    assert html.find(f'a[href="{external_link.url}"]', containing=external_link.name)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name,reverse_path,text",
    (
        ("inventory", "inventory:product_search", "Inventory"),
        ("orders", "orders:index", "Orders"),
        ("labelmaker", "labelmaker:index", "Labelmaker"),
        ("fba", "fba:index", "FBA"),
        ("purchases", "purchases:product_search", "Purchases"),
        ("channels", "channels:index", "Channels"),
        ("reports", "reports:index", "Reports"),
        ("admin", "admin:index", "Admin"),
    ),
)
def test_group_dependant_main_nav_links(group_name, reverse_path, text, user, get_html):
    group, _ = Group.objects.get_or_create(name=group_name)
    group.user_set.add(user)
    html = get_html()
    print(user)
    print(html)
    main_navigation = html.find('div[class="main_navigation"]')[0]
    assert main_navigation.find(f'a[href="{reverse(reverse_path)}"]', containing=text)
