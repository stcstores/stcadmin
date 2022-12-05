import pytest
from django.utils.safestring import SafeString

from home.templatetags import stcadmin_extras


@pytest.fixture(scope="module")
def title():
    return "Test Title"


@pytest.fixture
def text():
    return "Test Text"


@pytest.fixture
def tooltip(title, text):
    return stcadmin_extras.tooltip(title=title, text=text)


def test_returns_safe_string(tooltip):
    assert isinstance(tooltip, SafeString)


def test_contains_class(tooltip):
    assert 'class="tooltip' in tooltip


def test_contains_title(tooltip, title):
    assert f'tooltiptitle="{title}' in tooltip


def test_contains_text(tooltip, text):
    assert f'tooltiptext="{text}"' in tooltip
