"""The Products class provides methods for interacting with the inventory."""
from ccapi import CCAPI


class Products:
    """The Products class provides methods for interacting with the inventory."""

    @classmethod
    def get_ranges(cls, search_text):
        """Return Product Ranges according to submitted data."""
        search_result = CCAPI.search_products(search_text)
        range_ids = list(set([result.id for result in search_result]))
        ranges = [CCAPI.get_range(range_id) for range_id in range_ids]
        return ranges

    @classmethod
    def filter_end_of_line(cls, ranges):
        """Filter results according to the end of line value."""
        return [r for r in ranges if not r.end_of_line]

    @classmethod
    def filter_not_end_of_line(cls, ranges):
        """Return products that are in products but not end of line."""
        return [r for r in ranges if r.end_of_line]

    @classmethod
    def advanced_get_ranges(
        cls, search_text="", only_in_stock=False, option_matches_id=None
    ):
        """Return the results of an inventory search using the get_ranges method."""
        return CCAPI.get_ranges(
            search_text=search_text,
            only_in_stock=only_in_stock,
            option_matches_id=option_matches_id,
        )

    @classmethod
    def get_product_options(cls):
        """Return all Cloud Commerce product options."""
        return CCAPI.get_product_options()
