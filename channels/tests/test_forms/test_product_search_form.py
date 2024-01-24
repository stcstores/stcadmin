from unittest import mock

from channels.forms import ProductSearchForm


# Test Attributes
def test_has_all_attribute():
    assert ProductSearchForm.ALL == "all"


def test_has_created_attribute():
    assert ProductSearchForm.CREATED == "created"


def test_has_not_created_attribute():
    assert ProductSearchForm.NOT_CREATED == "not created"


def test_has_list_filter_default_attribute():
    assert ProductSearchForm.LISTED_FILTER_DEFAULT == ProductSearchForm.ALL


# Test Methods


@mock.patch("channels.forms.ProductRange")
def test_query_ranges_method(mock_product_range):
    products = mock.Mock()
    form = ProductSearchForm()
    value = form._query_ranges(products)
    products.values_list.assert_called_once_with("product_range", flat=True)
    mock_product_range.ranges.filter.assert_called_once_with(
        pk__in=products.values_list.return_value.order_by.return_value.distinct.return_value,
        status=mock_product_range.COMPLETE,
    )
    assert value == mock_product_range.ranges.filter.return_value


def test_filter_listed_method_with_created():
    ranges = mock.Mock()
    form = ProductSearchForm()
    form.cleaned_data = {"listed": ProductSearchForm.CREATED}
    value = form._filter_listed(ranges)
    ranges.filter.assert_called_once_with(shopify_listing__isnull=False)
    assert value == ranges.filter.return_value


def test_filter_listed_method_with_not_created():
    ranges = mock.Mock()
    form = ProductSearchForm()
    form.cleaned_data = {"listed": ProductSearchForm.NOT_CREATED}
    value = form._filter_listed(ranges)
    ranges.filter.assert_called_once_with(shopify_listing__isnull=True)
    assert value == ranges.filter.return_value


def test_filter_listed_method_with_default():
    ranges = mock.Mock()
    form = ProductSearchForm()
    form.cleaned_data = {"listed": None}
    value = form._filter_listed(ranges)
    ranges.filter.assert_not_called()
    assert value == ranges


@mock.patch("channels.forms.BaseProduct")
def test_query_products_method(
    mock_base_product,
):
    form = ProductSearchForm()
    form.cleaned_data = {"search_term": None}
    value = form._query_products()
    qs = mock_base_product.objects.all.return_value
    qs.variations.assert_called_once_with()
    qs.variations.return_value.active.assert_called_once_with()
    active = qs.variations.return_value.active.return_value
    active.select_related.assert_called_once_with("product_range", "supplier")
    active.select_related.return_value.prefetch_related.assert_called_once_with(
        "variation_option_values",
        "variation_option_values__variation_option",
        "shopify_listing",
    )
    active.select_related.return_value.prefetch_related.return_value.order_by.assert_called_once_with(
        "product_range__name"
    )
    assert (
        value
        == active.select_related.return_value.prefetch_related.return_value.order_by.return_value
    )


@mock.patch("channels.forms.BaseProduct")
def test_query_products_method_filters_products_with_search_term(mock_base_product):
    form = ProductSearchForm()
    form.cleaned_data = {"search_term": "text"}
    form._query_products()
    mock_base_product.objects.text_search.assert_called_once_with("text")
    mock_base_product.objects.all.assert_not_called()


@mock.patch("channels.forms.BaseProduct")
def test_query_products_method_does_not_filter_products_without_search_term(
    mock_base_product,
):
    form = ProductSearchForm()
    form.cleaned_data = {"search_term": None}
    form._query_products()
    mock_base_product.objects.text_search.assert_not_called()
    mock_base_product.objects.all.assert_called_once_with()


@mock.patch("channels.forms.Count")
@mock.patch("channels.forms.ProductSearchForm._query_products")
@mock.patch("channels.forms.ProductSearchForm._filter_listed")
@mock.patch("channels.forms.ProductSearchForm._query_ranges")
def test_save_method(
    mock_query_ranges, mock_filter_listed, mock_query_products, mock_count
):
    form = ProductSearchForm()
    form.save()
    mock_query_products.assert_called_once_with()
    mock_query_ranges.assert_called_once_with(mock_query_products.return_value)
    mock_filter_listed.assert_called_once_with(mock_query_ranges.return_value)
    mock_filter_listed.return_value.order_by.assert_called_once_with("name")
    mock_count.assert_called_once_with("products")
    mock_filter_listed.return_value.order_by.return_value.annotate.assert_called_once_with(
        variation_count=mock_count.return_value
    )
    assert (
        form.ranges
        == mock_filter_listed.return_value.order_by.return_value.annotate.return_value
    )
