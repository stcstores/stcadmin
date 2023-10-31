from fba.models.shipments import shortened_description, shortened_description_list


def test_shortended_description_returns_empty_string_when_passed_none():
    assert shortened_description(None) == ""


def test_shortened_description_returns_input_if_less_than_max_length_chars():
    desc = "ABCDEFGHIJ"
    assert shortened_description(desc, max_length=10) == desc


def test_shortended_description_shortens_descriptions_longer_than_max_length():
    desc = "ABCDEFGHIJK"
    assert shortened_description(desc, max_length=10) == "ABCDEFG..."


def test_shortened_description_max_length_default():
    desc = "S" * 50
    assert len(shortened_description(desc)) == 30


def test_shortened_description_list_returns_emtpy_string_when_passed_emtpy_list():
    assert shortened_description_list([]) == ""


def test_shortened_description_list_return_value():
    descs = ["s" * 5, "a" * 5]
    expected = "aaaaa + 1 other items"
    assert shortened_description_list(descs) == expected


def test_shortened_description_list_shortens_descriptions():
    descs = ["s" * 14, "a" * 12]
    expected = "aaaaaaa... + 1 other items"
    assert shortened_description_list(descs, max_length=10) == expected
