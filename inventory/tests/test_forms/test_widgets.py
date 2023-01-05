import json

import pytest

from inventory.forms import widgets


@pytest.fixture
def selectize_options():
    return {"key": "value"}


def test_model_select2_createable_widget():
    context = widgets.ModelSelect2CreateableWidget().get_context(None, None, {})
    assert context["create_new_url"] == ""


def test_multiple_selectize_widget_sets_selectize_options(selectize_options):
    widget = widgets.MultipleSelectizeWidget(selectize_options=selectize_options)
    assert widget.selectize_options == selectize_options


def test_multiple_selectize_widget_get_context_method(selectize_options):
    widget = widgets.MultipleSelectizeWidget(selectize_options=selectize_options)
    context = widget.get_context(None, None, {})
    assert str(context["widget"]["selectize_options"]) == json.dumps(selectize_options)


def test_single_selectize_widget_sets_selectize_options(selectize_options):
    widget = widgets.SingleSelectizeWidget(selectize_options=selectize_options)
    assert widget.selectize_options == selectize_options


def test_single_selectize_widget_get_context_method(selectize_options):
    widget = widgets.SingleSelectizeWidget(selectize_options=selectize_options)
    context = widget.get_context(None, None, {})
    assert str(context["widget"]["selectize_options"]) == json.dumps(selectize_options)


def test_selectize_model_multiple_choice_widget_get_context_method():
    widget = widgets.SelectizeModelMultipleChoiceWidget()
    context = widget.get_context(None, None, {})
    assert str(context["widget"]["selectize_options"]) == json.dumps(
        widget.selectize_options
    )
