from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from home.views import UserInGroupMixin
from spring_manifest import forms
from spring_manifest import models
from django.db.models import Q
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from spring_manifest.forms import SpringManifestForm


class SpringUserMixin(UserInGroupMixin):
    groups = ['spring']


class Index(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/index.html'


class SpringManifestSuccessView(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/spring_manifest_success.html'


class SpringManifestView(SpringUserMixin, FormView):
    template_name = 'spring_manifest/spring_manifest.html'
    success_url = reverse_lazy('spring_manifest:spring_manifest_success')
    form_class = SpringManifestForm

    def form_valid(self, form):
        incomplete_countries = models.CloudCommerceCountryID.objects.filter(
            Q(iso_code='') | Q(zone=None)).count()
        if incomplete_countries > 0:
            return redirect(reverse_lazy('spring_manifest:country_errors'))
        for manifest in form.manifests:
            manifest.file_manifest()
        return super().form_valid(form)


class CountryErrors(SpringUserMixin, FormView):
    template_name = 'spring_manifest/country_errors.html'
    form_class = forms.CloudCommerceCountryIDFormSet
    success_url = reverse_lazy('spring_manifest:spring_manifest')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = models.CloudCommerceCountryID.objects.filter(
            Q(iso_code='') | Q(zone=None))
        return kwargs

    def form_valid(self, form):
        for country_form in form:
            country_form.save()
        return super().form_valid(form)
