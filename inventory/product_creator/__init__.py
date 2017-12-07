from . single_product import SingleProduct  # noqa
from . variation_product import VariationProduct  # noqa


def create_variations(new_product):
    new_product.create_products()
