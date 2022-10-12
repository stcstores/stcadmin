from unittest.mock import Mock, call

import pytest

from reports import models


def test_report_generator_has_download_model_attribute():
    download_object = Mock()
    generator = models.BaseReportGenerator(download_object=download_object)
    assert generator.download_object == download_object


def test_base_report_generator_get_row_kwargs_raises_not_implemented():
    generator = models.BaseReportGenerator(download_object=Mock())
    with pytest.raises(NotImplementedError):
        generator.get_row_kwargs()


def test_base_report_generator_make_row_raises_not_implemented():
    generator = models.BaseReportGenerator(download_object=Mock())
    with pytest.raises(NotImplementedError):
        generator.get_row_kwargs()


def test_base_report_generator_generate_method_calls_get_row_kwargs():
    generator = models.BaseReportGenerator(download_object=Mock())
    mock_get_row_kwargs = Mock(return_value=({}))
    mock_make_row = Mock()
    generator.get_row_kwargs = mock_get_row_kwargs
    generator.make_row = mock_make_row
    generator._generate()
    mock_get_row_kwargs.assert_called_once_with()


def test_base_report_generator_generate_method_calls_make_row():
    generator = models.BaseReportGenerator(download_object=Mock())
    mock_get_row_kwargs = Mock(return_value=({"n": 1}, {"n": 2}, {"n": 3}))
    mock_make_row = Mock(return_value=Mock())
    generator.get_row_kwargs = mock_get_row_kwargs
    generator.make_row = mock_make_row
    generator._generate()
    mock_make_row.assert_has_calls((call(n=1), call(n=2), call(n=3)), any_order=False)


def test_base_report_generator_generate_method_returns_rows():
    generator = models.BaseReportGenerator(download_object=Mock())
    mock_get_row_kwargs = Mock(return_value=({"n": 1}, {"n": 2}, {"n": 3}))
    make_row_return_values = [Mock(), Mock(), Mock()]
    mock_make_row = Mock(side_effect=make_row_return_values)
    generator.get_row_kwargs = mock_get_row_kwargs
    generator.make_row = mock_make_row
    assert generator._generate() == make_row_return_values


def test_base_report_generator_make_rows_method():
    records = [
        {"row1": 1, "row2": 2, "row3": 3},
        {"row1": 4, "row2": 5, "row3": 6},
        {"row1": 7, "row2": 8, "row3": 9},
    ]
    generator = models.BaseReportGenerator(download_object=Mock())
    generator.header = ["row1", "row2", "row3"]
    assert generator.make_rows(records) == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def test_base_report_generator_generate_csv_method():
    records = [
        {"row1": 1, "row2": 2, "row3": 3},
        {"row1": 4, "row2": 5, "row3": 6},
        {"row1": 7, "row2": 8, "row3": 9},
    ]
    generator = models.BaseReportGenerator(download_object=Mock())
    generator.header = ["row1", "row2", "row3"]
    generator._generate = Mock(return_value=records)
    assert generator.generate_csv() == "row1,row2,row3\r\n1,2,3\r\n4,5,6\r\n7,8,9\r\n"


class TestReportGenerator(models.BaseReportGenerator):
    header = ["row1", "row2", "row3"]

    def get_row_kwargs(self):
        n = self.download_object.start_number
        for _ in range(3):
            yield {"number": n}
            n += 3

    def make_row(self, **kwargs):
        return {
            "row1": kwargs["number"],
            "row2": kwargs["number"] + 1,
            "row3": kwargs["number"] + 2,
        }


def test_report_generator_subclass():
    download_object = Mock(start_number=1)
    expected = "row1,row2,row3\r\n1,2,3\r\n4,5,6\r\n7,8,9\r\n"
    assert TestReportGenerator(download_object).generate_csv() == expected
