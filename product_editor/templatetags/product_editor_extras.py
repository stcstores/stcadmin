"""Template tags for Product Editor."""

from django import template

import product_editor.editor_manager.manager

register = template.Library()


@register.simple_tag
def new_product_url():
    """Get URL for the new product creator landing page."""
    return product_editor.editor_manager.manager.NewProductManager.landing_page()


@register.simple_tag
def edit_product_url(range_id):
    """Get URL for the edit product landing page."""
    return product_editor.editor_manager.manager.EditProductManager.landing_page(
        range_id
    )
