"""Forms for product search page."""

from ccapi import CCAPI
from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from product_editor.forms.widgets import HorizontalRadio


class OptionSelectField(forms.MultiValueField):
    """Field for selecting a Product Option value to search by."""

    def __init__(self, *args, **kwargs):
        """Add sub fields."""
        self.option_choices = kwargs.pop("option_choices")
        self.option_value_choices = kwargs.pop("option_value_choices")
        self.option_matches = kwargs.pop("option_matches")
        fields = (
            forms.ChoiceField(choices=self.option_choices),
            forms.ChoiceField(choices=self.option_value_choices),
        )
        kwargs["widget"] = OptionSelectWidget(
            None,
            option_choices=self.option_choices,
            option_value_choices=self.option_value_choices,
            option_matches=self.option_matches,
        )
        super().__init__(fields=fields, require_all_fields=False, *args, **kwargs)

    def compress(self, value):
        """Return value as a list."""
        if len(value) == 0:
            return None
        return int(value[1])


class OptionSelectWidget(forms.widgets.MultiWidget):
    """Widget for OptionSelectField."""

    template_name = "product_editor/widgets/option_select_widget.html"

    def __init__(self, *args, **kwargs):
        """Add sub widgets."""
        self.option_choices = kwargs.pop("option_choices")
        self.option_value_choices = kwargs.pop("option_value_choices")
        self.option_matches = kwargs.pop("option_matches")
        _widgets = [
            forms.Select(choices=self.option_choices),
            forms.Select(choices=self.option_value_choices),
        ]
        super().__init__(_widgets, *args, **kwargs)

    def decompress(self, value):
        """Decompress value."""
        if value is not None and "" not in value:
            return value
        return [None, None]

    def render(self, name, value, attrs=None, renderer=None):
        """Return widget as rendered HTML."""
        values = self.decompress(value)
        final_attrs = self.build_attrs(attrs)
        final_attrs["required"] = False
        id_ = final_attrs.get("id")
        widgets = []
        for i, widget in enumerate(self.widgets):
            widget_attrs = dict(final_attrs, id="%s_%s" % (id_, i))
            widget_name = name + "_%s" % i
            rendered_widget = widget.render(widget_name, values[i], widget_attrs)
            widgets.append(rendered_widget)
        html = render_to_string(
            self.template_name,
            {
                "widgets": widgets,
                "name": name,
                "id": id_,
                "option_matches": self.option_matches,
            },
        )
        return mark_safe(html)


class ProductSearchForm(forms.Form):
    """Product search form."""

    EXCLUDE = "exclude"
    INCLUDE = "include"
    EXCLUSIVE = "exclusive"
    END_OF_LINE_CHOICES = (
        (EXCLUDE, "Exclude"),
        (INCLUDE, "Include"),
        (EXCLUSIVE, "Exclusive"),
    )

    BASIC = "basic"
    ADVANCED = "advanced"

    SEARCH_TYPE_CHOICES = ((BASIC, "Basic"), (ADVANCED, "Advanced"))

    search_type_help_text = (
        "Select a Search Type<ul><li><b>Basic Search:"
        "</b>A quick easy search which returns a limited number of items</li>"
        "<li><b>Advanced Search:</b> More options for a refined search."
        "Will return all possible products."
    )

    basic_search_matches = (
        "SKU",
        "Title",
        "Barcode",
        "Linnworks SKU",
        "Linnworks Title",
        "Supplier",
        "Supplier SKU",
        "All Product Options",
    )
    basic_search_help_text = "Matches:<ul>{}</ul>".format(
        "".join(["<li>{}</li>".format(text) for text in (basic_search_matches)])
    )

    advanced_search_matches = ("SKU", "Title")
    advanced_search_help_text = "Matches:<ul>{}</ul>".format(
        "".join(["<li>{}</li>".format(text) for text in (advanced_search_matches)])
    )

    search_type = forms.ChoiceField(
        required=True,
        label="Search Type",
        help_text=search_type_help_text,
        initial=BASIC,
        choices=SEARCH_TYPE_CHOICES,
        widget=forms.RadioSelect(),
    )

    end_of_line = forms.ChoiceField(
        widget=HorizontalRadio(),
        choices=END_OF_LINE_CHOICES,
        required=False,
        label="Hide End of Line",
        help_text="Hide End of Line Episodes",
        initial=EXCLUDE,
    )

    basic_search_text = forms.CharField(
        label="Basic Search",
        required=False,
        help_text=basic_search_help_text,
        widget=forms.TextInput(attrs={"class": "basic_search"}),
    )

    advanced_search_text = forms.CharField(
        label="Search Text",
        required=False,
        help_text=advanced_search_help_text,
        widget=forms.TextInput(attrs={"class": "advanced_search"}),
    )

    advanced_hide_out_of_stock = forms.BooleanField(
        required=False,
        label="Hide Out of Stock",
        help_text="Hide ranges with no items in stock.",
    )

    selectable_options = [
        "WooCategory1",
        "WooCategory2",
        "WooCategory3",
        "Manufacturer",
        "Brand",
        "Supplier",
        "Discontinued",
        "Package Type",
        "International Shipping",
    ]

    def __init__(self, *args, **kwargs):
        """Add advanced option field."""
        super().__init__(*args, **kwargs)
        option_data = CCAPI.get_product_options()
        option_choices = [("", "")]
        option_value_choices = [("", "")]
        option_matches = {}
        for option in option_data:
            if option.option_name in self.selectable_options:
                option_choices.append((option.id, option.option_name))
                option_matches[option.id] = []
                for value in option.values:
                    option_value_choices.append((value.id, value.value))
                    option_matches[option.id].append(value.id)
        option_choices.sort(key=lambda x: x[1])
        option_value_choices.sort(key=lambda x: x[1])
        self.fields["advanced_option"] = OptionSelectField(
            label="Product Option",
            required=False,
            help_text="Search for products with a particular <b>Product Option</b>",
            option_choices=option_choices,
            option_value_choices=option_value_choices,
            option_matches=option_matches,
        )

    def clean(self):
        """Clean submitted data."""
        cleaned_data = super().clean()
        if cleaned_data.get("search_type") == self.BASIC:
            cleaned_data = self.clean_basic_search(cleaned_data)
        elif cleaned_data.get("search_type") == self.ADVANCED:
            cleaned_data = self.clean_advanced_search(cleaned_data)
        else:
            raise ValidationError("No valid search type supplied.")
        self.filter_end_of_line(cleaned_data)
        self.ranges.sort(key=lambda x: x.name)
        return cleaned_data

    def filter_end_of_line(self, cleaned_data):
        """Filter results according to the end of line value."""
        if cleaned_data["end_of_line"] == self.EXCLUDE:
            self.ranges = [r for r in self.ranges if not r.end_of_line]
        elif cleaned_data["end_of_line"] == self.EXCLUSIVE:
            self.ranges = [r for r in self.ranges if r.end_of_line]

    def clean_basic_search(self, data):
        """Add ranges according to basic search text."""
        self.ranges = self.get_ranges(data["basic_search_text"])
        return data

    def clean_advanced_search(self, data):
        """Add ranges according to advanced search."""
        search_text = data.get("advanced_search_text")
        option_id = data.get("advanced_option")
        if not search_text and not option_id:
            raise ValidationError(
                "Either search text or an option must be supplied for "
                "Advanced Search"
            )
        kwargs = {
            "search_text": search_text,
            "only_in_stock": data["advanced_hide_out_of_stock"],
            "option_matches_id": option_id,
        }
        self.ranges = CCAPI.get_ranges(**kwargs)
        return data

    def get_ranges(self, search_text):
        """Return Product Ranges according to submitted data."""
        search_result = CCAPI.search_products(search_text)
        range_ids = list(set([result.id for result in search_result]))
        ranges = [CCAPI.get_range(range_id) for range_id in range_ids]
        return ranges
