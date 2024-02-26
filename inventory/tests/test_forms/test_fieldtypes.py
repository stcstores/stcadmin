import pytest
from django.core.exceptions import ValidationError

from inventory.forms.fieldtypes import Validators


@pytest.mark.parametrize(
    "value,allowed_characters,error",
    (
        ("a", [], False),
        ("a", [], False),
        ("$", [], True),
        ("$", ["$"], False),
        (" ", [], False),
    ),
)
def test_allow_characters_method(value, allowed_characters, error):
    if error:
        with pytest.raises(ValidationError):
            Validators.allow_characters(value, allowed_characters)
    else:
        Validators.allow_characters(value, allowed_characters)
