"""Forms for manifest app."""

from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from spring_manifest import models


class BasePackageFormset(BaseInlineFormSet):
    """Base form set for packages."""

    def add_fields(self, form, index):
        """Add nested form."""
        super(BasePackageFormset, self).add_fields(form, index)

        form.nested = ItemFormset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='item-%s-%s' %
            (form.prefix, ItemFormset.get_default_prefix()))

    def is_valid(self):
        """Return True if all forms are valid."""
        result = super().is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result

    def save(self, commit=True):
        """Update database."""
        result = super().save(commit=commit)
        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)
        return result

    def add_package(self):
        """Create new package for order."""
        existing_packages = self.instance.manifestpackage_set.all()
        package_number = max([p.package_number for p in existing_packages]) + 1
        package = models.ManifestPackage(
            order=self.instance, package_number=package_number)
        package.save()
        for item in existing_packages[0].manifestitem_set.all():
            new_item = models.ManifestItem(
                item_id=item.item_id, package=package, quantity=0)
            new_item.save()

    def clear_empty_packages(self):
        """Remove packages with not items."""
        packages = self.instance.manifestpackage_set.all()
        for package in packages:
            if sum([i.quantity for i in package.manifestitem_set.all()]) == 0:
                package.delete()


class UpdateOrderForm(forms.ModelForm):
    """Form for updating manifest orders."""

    class Meta:
        """Set model and fields."""

        model = models.ManifestOrder
        fields = ['country', 'service']

    def save(self, commit=True):
        """Update database."""
        order = super().save(commit=False)
        if 'service' in self.changed_data:
            order.manifest = models.get_manifest_by_service(
                self.data['service'])
        if 'delay' in self.data:
            order.manifest = None
        elif 'cancel' in self.data:
            order.manifest = None
            order.canceled = True
        elif 'uncancel' or 'undelay' in self.data:
            order.manifest = models.get_manifest_by_service(order.service)
            order.canceled = False
        return super().save(commit=commit)


class ManifestItemForm(forms.ModelForm):
    """Form for updating manifest items."""

    class Meta:
        """Set models and fields."""

        model = models.ManifestItem
        fields = ('quantity', 'item_id')


ItemFormset = inlineformset_factory(
    models.ManifestPackage,
    models.ManifestItem,
    fields=('quantity', 'item_id'),
    extra=0,
    can_delete=False,
    form=ManifestItemForm)

PackageFormset = inlineformset_factory(
    models.ManifestOrder,
    models.ManifestPackage,
    formset=BasePackageFormset,
    fields=('package_number', ),
    extra=0,
    can_delete=False)
