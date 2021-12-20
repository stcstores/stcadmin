"""KwargFormSet class."""

from django.forms.formsets import BaseFormSet
from django.forms.renderers import get_default_renderer


class KwargFormSet(BaseFormSet):
    """Base class for formsets allowing kwargs to be passed to each form."""

    extra = 0
    can_order = False
    can_delete = False
    renderer = get_default_renderer()

    def __init__(self, *args, **kwargs):
        """Set formset attributes."""
        self.form_kwargs = kwargs["form_kwargs"]
        self.min_num = len(self.form_kwargs)
        self.max_num = self.min_num
        self.absolute_max = self.max_num
        super().__init__(*args, **kwargs)

    def validate_max(self):
        """Return True if number of forms is equal to min_num."""
        return len(self.forms) == self.min_num

    def validate_min(self):
        """Return True if number of forms is equal to max_num."""
        return len(self.forms) == self.min_num

    def get_form_kwargs(self, i):
        """Return kwargs for formset i."""
        return self.form_kwargs[i]

    def _construct_form(self, i, **kwargs):
        """Instantiate and return the i-th form instance in a formset."""
        defaults = {
            "auto_id": self.auto_id,
            "prefix": self.add_prefix(i),
            "error_class": self.error_class,
            "use_required_attribute": False,
            "renderer": self.renderer,
        }
        defaults.update(self.get_form_kwargs(i))
        if self.is_bound:
            defaults["data"] = self.data
            defaults["files"] = self.files
        if self.initial and "initial" not in kwargs:
            try:
                defaults["initial"] = self.initial[i]
            except IndexError:
                pass
        if i >= self.initial_form_count() and i >= self.min_num:
            defaults["empty_permitted"] = True
        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)
        return form
