from unittest import mock

import pytest

from home.templatetags import stcadmin_extras


@pytest.fixture
def field():
    field = mock.Mock()
    field.field.widget.attrs = {}
    return field


def test_returns_input(field):
    assert stcadmin_extras.add_class(field, "newClass") == field


def test_sets_class(field):
    stcadmin_extras.add_class(field, "newClass")
    assert field.field.widget.attrs["class"] == "newClass"


def test_adds_class(field):
    field.field.widget.attrs["class"] = "classOne classTwo"
    stcadmin_extras.add_class(field, "newClass")
    assert field.field.widget.attrs["class"] == "classOne classTwo newClass"
