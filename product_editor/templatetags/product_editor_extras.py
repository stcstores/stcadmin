"""Template tags for Product Editor."""

from django import template

from product_editor.editor_manager.manager import (EditProductManager,
                                                   NewProductManager)

register = template.Library()


@register.simple_tag
def new_product_url():
    """Get URL for the new product creator landing page."""
    return NewProductManager.landing_page()


@register.simple_tag
def edit_product_url(range_id):
    """Get URL for the edit product landing page."""
    return EditProductManager.landing_page(range_id)
