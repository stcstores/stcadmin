"""Template tags for the Validation app."""
from django import template
from django.template import loader

register = template.Library()


@register.simple_tag(takes_context=False)
def validation_table_group(group_name, stats, errors, group_name_url=None):
    """Render a validation error table."""
    t = loader.get_template("validation/validation_table_group.html")
    return t.render(
        {
            "group_name": group_name,
            "stats": stats,
            "errors": errors,
            "group_name_url": group_name_url,
        }
    )


@register.simple_tag(takes_context=False)
def validation_error_row(error):
    """Render a validation error table row."""
    t = loader.get_template("validation/validation_error_row.html")
    return t.render({"error": error})


@register.simple_tag(takes_context=False)
def validation_stats(stats):
    """Render the stats for a group of validation errors."""
    t = loader.get_template("validation/validation_stats.html")
    return t.render({"stats": stats})
