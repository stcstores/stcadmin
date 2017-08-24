from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect
from cloud_commerce . forms import NewVariationProductForm, VariationFormSet
from cloud_commerce . product_creator import VariationProduct
from . views import CloudCommerceUserMixin


class VariationFormWizard(CloudCommerceUserMixin, SessionWizardView):

    form_list = [
        NewVariationProductForm, VariationFormSet]

    TEMPLATES = {
        '0': 'cloud_commerce/variation_form_setup.html',
        '1': 'cloud_commerce/variation_table_form.html'}

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def post(self, *args, **kwargs):
        go_to_step = self.request.POST.get('wizard_goto_step', None)
        form = self.get_form(data=self.request.POST, files=self.request.FILES)
        if form.is_valid():
            current_index = self.get_step_index(self.steps.current)
            goto_index = self.get_step_index(go_to_step)

            if current_index > goto_index:
                if form.is_valid():
                    self.storage.set_step_data(
                        self.steps.current, self.process_step(form))
                    self.storage.set_step_files(
                        self.steps.current, self.process_step_files(form))
        return super().post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        new_product = VariationProduct(form_list)
        return redirect(
            'inventory:product_range', new_product.product_range.id)

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '1':
            cleaned_data = self.get_cleaned_data_for_step('0')
            selected_options = cleaned_data['selected_options']
            variations = cleaned_data['variations']
            if data is not None:
                data = self.remove_unused_variations(
                    data, selected_options, variations)
            selected_variables = cleaned_data['selected_variables']
            form.initial = self.initial_for_variation_table_form(
                    selected_variables, variations)
            for var_form in form.forms:
                var_form.set_variation_fields(
                    selected_options, selected_variables)
                var_form.department = cleaned_data['department']
        return form

    def remove_unused_variations(
            self, data, selected_options, existant_variations):
        forms = self.get_variation_values_from_variation_table_data(
                data, selected_options)
        fields_to_delete = []
        for form_number, variations in forms.items():
            if not self.variation_required(variations, existant_variations):
                fields_to_delete += [
                    item for item in data if item[2] == form_number]
        return {key: value for key, value in data.items()
                if key not in fields_to_delete}

    def get_variation_values_from_variation_table_data(
            self, data, selected_options):
        forms = {}
        for key, value in data.items():
            if key[0] == '2' and key[2].isdigit():
                form_number = key.split('-')[1]
                forms[form_number] = {
                    field: value for field in selected_options}
        return forms

    def variation_required(self, form_variations, existant_variations):
        for existing_variation in existant_variations:
            shared_items = set(
                form_variations.items()) & set(existing_variation.items())
            if len(shared_items) == len(form_variations):
                return True
        return False

    def initial_for_variation_table_form(self, selected_variables, variations):
        return [
            {**variation, **selected_variables} for variation in variations]
