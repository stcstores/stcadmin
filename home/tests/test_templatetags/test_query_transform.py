from unittest import mock

import pytest
from django.http import QueryDict

from home.templatetags import stcadmin_extras


@pytest.fixture
def get():
    query_dict = QueryDict("", mutable=True)
    query_dict.update({"page": [2]})
    return query_dict


@pytest.fixture
def context(get):
    return {"request": mock.Mock(GET=get)}


@pytest.fixture
def kwargs():
    return {"otherparameter": "sometext"}


@pytest.fixture
def transformed_query(context, kwargs):
    return stcadmin_extras.query_transform(context, **kwargs)


def test_returns_url_encoded_query(transformed_query):
    assert transformed_query == "page=%5B2%5D&otherparameter=sometext"
