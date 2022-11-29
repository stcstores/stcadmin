import pytest

from home import models


@pytest.fixture
def external_link(external_link_factory):
    external_link = external_link_factory.create()
    external_link.full_clean()
    return external_link


@pytest.fixture
def new_external_link():
    external_link = models.ExternalLink(name="Test Link", url="example.com/test")
    external_link.save()
    return external_link


@pytest.mark.django_db
def test_has_name_attribute(external_link):
    assert isinstance(external_link.name, str)
    assert len(external_link.name) > 0


@pytest.mark.django_db
def test_has_url_attribute(external_link):
    assert isinstance(external_link.url, str)
    assert len(external_link.url) > 0


@pytest.mark.django_db
def test_has_ordering_attribute(external_link):
    assert isinstance(external_link.ordering, int)


@pytest.mark.django_db
def test_ordering_defaut(new_external_link):
    assert new_external_link.ordering == 100
