"""Base classes for product fields."""

from inspect import isclass

from django import forms
from django.core.exceptions import ValidationError

from . import widgets


class Validators:
    """Holder class for validation methods."""

    @staticmethod
    def alphanumeric(value):
        """Validate every character in value is alphanumeric."""
        if isinstance(value, list):
            for v in value:
                Validators.alphanumeric(v)
        else:
            valid = True
            for char in str(value):
                if char.isalnum() or char == " ":
                    continue
                valid = False
                break
            if valid is False:
                raise ValidationError("Only alphanumeric characters are allowed.")

    @staticmethod
    def numeric(value):
        """Validate every character in value is numeric."""
        if not value.isdigit():
            raise ValidationError('"{}" is not a valid a integer.')

    @staticmethod
    def allow_characters(value, allowed_characters):
        """Raise ValidationError if any illegal characters are in value."""
        error_message = (
            "Allowed characters are letters, numbers or {}."
            "The following characters where found: {}."
        )
        errors = [
            char
            for char in value
            if not char.isalnum() and char != " " and char not in allowed_characters
        ]
        if len(errors) > 0:
            str_allowed_characters = ", ".join(allowed_characters)
            str_errors = ", ".join(errors)
            raise ValidationError(
                error_message.format(str_allowed_characters, str_errors)
            )

    @staticmethod
    def disallow_characters(value, disallowed_characters):
        """Raise ValidationError if any disallowed characters are in value."""
        error_message = (
            "The characters {} are not allowed in this field."
            "The following characters where found: {}."
        )
        errors = [char for char in value if char in disallowed_characters]
        if len(errors) > 0:
            str_disallowed_characters = ", ".join(disallowed_characters)
            str_errors = ", ".join(errors)
            raise ValidationError(
                error_message.format(str_disallowed_characters, str_errors)
            )


class FormField(forms.Field):
    """Base class for product fields."""

    label = None
    name = None
    field = None
    variable = False
    variation = False
    must_vary = False
    help_text = None
    placeholder = None
    html_class = None
    size = None
    small_size = None
    initial = None
    required_message = ""
    validators = []
    allowed_characters = None
    disallowed_characters = None

    def __init__(self, *args, **kwargs):
        """Set field attributes."""
        self.kwargs = self.get_field_kwargs(*args, **kwargs)
        super().__init__(*args, **self.kwargs)
        self.set_error_messages()
        self.set_widget()

    def get_field_kwargs(self, *args, **kwargs):
        """Return the kwargs for the field."""
        if "required" not in kwargs:
            kwargs["required"] = self.is_required
        else:
            kwargs["required"] = False
        if "small" in kwargs:
            if kwargs["small"] is True:
                self.size = self.small_size
            kwargs.pop("small")
        kwargs["label"] = self.label
        kwargs["help_text"] = self.help_text
        kwargs["validators"] = self.validators
        if self.initial is not None:
            kwargs["initial"] = self.initial
        return kwargs

    def set_widget(self):
        """Set the field's widget."""
        if "html_class" in self.kwargs:
            self.html_class = self.kwargs.pop("html_class")
        attrs = self.get_widget_attrs()
        if isclass(self.widget):
            self.widget = self.widget(attrs)
        else:
            self.widget = self.widget.__class__(attrs)

    def set_error_messages(self):
        """Set the field's error messages."""
        if self.is_required:
            self.error_messages["required"] = self.required_message

    @property
    def is_required(self):
        """Return True if field is required, else False."""
        if len(self.required_message) > 0:
            return True
        return False

    def get_widget_attrs(self):
        """Return widget for field."""
        attrs = {}
        if self.placeholder is not None:
            attrs["placeholder"] = self.placeholder
        if self.html_class is not None:
            attrs["class"] = self.html_class
        if self.size is not None:
            attrs["size"] = self.size
        if self.is_required:
            attrs["required"] = "true"
        return attrs

    def validate(self, value):
        """Limit characters if disallowed_characters is set."""
        super().validate(value)
        if self.disallowed_characters is not None:
            Validators.disallow_characters(value, self.disallowed_characters)
        if self.allowed_characters is not None:
            Validators.allow_characters(value, self.allowed_characters)
        for validator in self.validators:
            validator(value)


class ChoiceField(FormField, forms.ChoiceField):
    """Base class for product fields inheriting from ChoiceField."""

    variable = False
    variation = False
    must_vary = False
    size = None
    small_size = None

    def __init__(self, *args, **kwargs):
        """Set field attributes."""
        if "choices" not in kwargs:
            kwargs["choices"] = self.get_choices()
        kwargs["label"] = self.label
        kwargs = super().__init__(*args, **kwargs)


class BaseSelectizeField(FormField):
    """Base class for choice fields using selectize.js."""

    selectize_options = {}

    def __init__(self, *args, **kwargs):
        """Set field attributes."""
        self.choices = kwargs.get("choices") or ()
        if "label" in kwargs:
            self.label = kwargs.pop("label")
        kwargs = super().__init__(*args, **kwargs)

    def get_widget(self, choices=None):
        """Return widget for field."""
        attrs = {}
        if self.placeholder is not None:
            attrs["placeholder"] = self.placeholder
        if self.html_class is not None:
            attrs["class"] = self.html_class
        if self.size is not None:
            attrs["size"] = self.size
        return self.widget_class(
            attrs=attrs, selectize_options=self.selectize_options, choices=()
        )


class SelectizeField(BaseSelectizeField, forms.MultipleChoiceField):
    """Base class for selectize fields allowing multiple values."""

    widget_class = widgets.MultipleSelectizeWidget

    def __init__(self, *args, **kwargs):
        """Create the field and widget."""
        super(BaseSelectizeField, self).__init__(*args, **kwargs)
        super(forms.MultipleChoiceField, self).__init__(*args, **kwargs)
        if "choices" not in kwargs:
            kwargs["choices"] = self.get_choices()
        self.widget = self.get_widget()
        self.widget.choices = kwargs["choices"]

    def to_python(self, *args, **kwargs):
        """Return submited values as a list."""
        value = super().to_python(*args, **kwargs)
        if isinstance(value, str):
            return value.split(",")
        return value


class SingleSelectize(BaseSelectizeField, forms.ChoiceField):
    """Base class for selectize fields allowing a single value."""

    widget_class = widgets.SingleSelectizeWidget
    selectize_options = {"maxItems": 1, "dropdownParent": "body"}

    def to_python(self, *args, **kwargs):
        """Return submitted value as a string."""
        value = super().to_python(*args, **kwargs)
        if isinstance(value, list):
            return value[0]
        return value


class SelectizeModelChoiceField(forms.ModelChoiceField, SingleSelectize):
    """Field allowing model objects to be selected with a Selectize widget."""

    def __init__(self, *args, **kwargs):
        """Create a ModelChoiceField with a Selectize widget."""
        if kwargs.get("required") is False:
            self.required_message = ""
        kwargs.update(self.get_field_kwargs(*args, **kwargs))
        if not args and not kwargs.get("queryset"):
            self.queryset = self.get_queryset()
        kwargs["empty_label"] = ""
        kwargs["widget"] = SingleSelectize.get_widget(self, choices=self.choices)
        forms.ModelChoiceField.__init__(self, self.queryset, **kwargs)


class NumberField(FormField, forms.IntegerField):
    """Base class for fields that only accept numeric values."""

    size = None
    small_size = None

    def to_python(self, value):
        """Clean submitted value."""
        value = super().to_python(value)
        if value in self.empty_values:
            return self.empty_value
        return value

    def clean(self, value):
        """If value is blank return zero."""
        value = super().clean(value)
        if not value:
            value = 0
        return value


class PriceField(FormField, forms.DecimalField):
    """Base class for product fields for handeling monetary values."""

    size = None
    small_size = None

    def __init__(self, *args, **kwargs):
        """Instanciate field."""
        FormField.__init__(self, *args, **kwargs)
        forms.DecimalField.__init__(self, max_digits=5, decimal_places=2)


class CheckboxField(FormField, forms.BooleanField):
    """Base class for product fields using a checkbox widget."""

    pass


class TextField(FormField, forms.CharField):
    """Base class for product fields using a text input."""

    def __init__(self, *args, **kwargs):
        """Instansiate object."""
        FormField.__init__(self, *args, **kwargs)
        forms.CharField.__init__(self, *args, **self.kwargs)

    def clean(self, value):
        """Clean whitespace from submitted value."""
        return super().clean(value).strip()


class TextareaField(FormField, forms.CharField):
    """Base class for product field using the textarea widget."""

    widget = forms.Textarea


class CombinationField(forms.MultiValueField):
    """Base class for product fields inheriting from MultiValueField."""

    help_text = ""

    def __init__(self, *args, **kwargs):
        """Prevent class attributes being lost during instantiation."""
        super().__init__(*args, **kwargs)
        self.help_text = self.__class__.help_text
        self.label = self.__class__.label
