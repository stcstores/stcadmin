"""Exceptions for product_editor."""


class VariationNotFoundError(ValueError):
    """Raised when a variation cannot be found in product form data."""

    def __init__(self, variation):
        """Raise exception."""
        super().__init__('Variation not found: {}'.format(variation))


class VariationKeyMissmatch(ValueError):
    """Raised when variation dicts have non matching keys."""

    def __init__(self, variations):
        """Raise exception."""
        super().__init__('Variation key missmatched: {}'.format(variations))
