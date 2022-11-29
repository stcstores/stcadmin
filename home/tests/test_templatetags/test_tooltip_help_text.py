from unittest import mock

import pytest

from home.templatetags import stcadmin_extras


@pytest.fixture
def label():
    return "Label Text"


@pytest.fixture
def help_text():
    return "Help Text"


@pytest.fixture
def field_with_help_text(label, help_text):
    return mock.Mock(label=label, help_text=help_text)


@pytest.fixture
def field_without_help_text(label):
    return mock.Mock(label=label, help_text="")


def test_returns_tooltip(field_with_help_text, label, help_text):
    tooltip = stcadmin_extras.tooltip(title=label, text=help_text)
    assert stcadmin_extras.tooltip_help_text(field_with_help_text) == tooltip


def test_returns_empty_string_if_help_text_is_empty(field_without_help_text):
    assert stcadmin_extras.tooltip_help_text(field_without_help_text) == ""


def test_returns_empty_string_if_field_is_none():
    assert stcadmin_extras.tooltip_help_text(None) == ""
