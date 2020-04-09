"""Forms for product search page."""

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Reset, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from inventory.models import Products


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


class AdvancedInventorySearchForm(forms.Form):
    """Product search form."""

    EXCLUDE = "exclude"
    INCLUDE = "include"
    EXCLUSIVE = "exclusive"
    END_OF_LINE_CHOICES = (
        (EXCLUDE, "Hide End of Line"),
        (INCLUDE, "Show End of Line"),
        (EXCLUSIVE, "Only Show End of Line"),
    )

    search_text_help_text = "Matches: SKU and product name"

    end_of_line = forms.ChoiceField(
        choices=END_OF_LINE_CHOICES,
        required=False,
        label="End of Line",
        initial=EXCLUDE,
    )

    search_text = forms.CharField(
        label="Search",
        required=False,
        help_text=search_text_help_text,
        widget=forms.TextInput(attrs={"class": "advanced_search"}),
    )

    hide_out_of_stock = forms.BooleanField(required=False, label="Hide Out of Stock")

    selectable_options = [
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
        option_data = Products.get_product_options()
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
        option_choices = sorted(option_choices, key=lambda x: x[1])
        option_value_choices = sorted(option_value_choices, key=lambda x: x[1])
        self.fields["option"] = OptionSelectField(
            label="Product Option",
            required=False,
            help_text="Search for products with a particular <b>Product Option</b>",
            option_choices=option_choices,
            option_value_choices=option_value_choices,
            option_matches=option_matches,
        )
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "mr-2"
        self.helper.help_text_inline = False
        self.helper.error_text_inline = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        Field("search_text"),
                        Field("end_of_line"),
                        Field("hide_out_of_stock"),
                        css_class="col-md-6",
                    ),
                    Div(
                        Field("option", css_class="custom-select mr-sm-2"),
                        css_class="col-md-4",
                    ),
                    css_class="row",
                ),
                css_class="container",
            ),
            Div(
                Div(
                    FormActions(
                        Submit("submit", "Submit", css_class="button white"),
                        Reset("reset", "Reset"),
                    ),
                    css_class="col-md-4",
                ),
                css_class="row",
            ),
        )

    def clean(self):
        """Clean submitted data."""
        cleaned_data = super().clean()
        ranges = self.get_ranges(cleaned_data)
        ranges = self.filter_end_of_line(ranges, cleaned_data.get("end_of_line"))
        ranges = sorted(ranges, key=lambda x: x.name)
        cleaned_data["ranges"] = ranges
        return cleaned_data

    def filter_end_of_line(self, ranges, end_of_line):
        """Filter results according to the end of line value."""
        if end_of_line == self.EXCLUDE:
            ranges = Products.filter_end_of_line(ranges)
        elif end_of_line == self.EXCLUSIVE:
            ranges = Products.filter_not_end_of_line(ranges)
        return ranges

    def get_ranges(self, data):
        """Add ranges according to advanced search."""
        search_text = data.get("search_text")
        option_id = data.get("option")
        only_in_stock = data["hide_out_of_stock"]
        if not search_text and not option_id:
            raise ValidationError(
                "Either search text or an option must be supplied for "
                "Advanced Search"
            )
        return Products.advanced_get_ranges(
            search_text=search_text,
            option_matches_id=option_id,
            only_in_stock=only_in_stock,
        )
