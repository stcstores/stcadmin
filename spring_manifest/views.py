from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from home.views import UserInGroupMixin
from spring_manifest import forms, models
from spring_manifest.forms import SpringManifestForm


class SpringUserMixin(UserInGroupMixin):
    groups = ['spring']


class Index(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/index.html'


class SpringManifestSuccessView(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/spring_manifest_success.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['manifest_file'] = self.request.GET.get('manifest_file', None)
        return context


class SpringManifestView(SpringUserMixin, FormView):
    template_name = 'spring_manifest/spring_manifest.html'
    form_class = SpringManifestForm
    success_url = reverse_lazy('spring_manifest:spring_manifest_success')

    def get_download_message(self, filepath):
        return mark_safe(
            '<script>manifest_url = "{}";</script>'.format(filepath))

    def get_status_message(self):
        manifests = (m for n, m in self.form.manifests.items())
        orders = []
        for manifest in manifests:
            orders += manifest.manifested_orders
        services = {
            code: 0 for code in list(set(o.service_code for o in orders))}
        for order in orders:
            services[order.service_code] += 1
        lines = []
        lines.append('{} total orders manifested.'.format(len(orders)))
        for service_code, count in services.items():
            lines.append('{} orders manifested with code {}'.format(
                count, service_code))
        return lines

    def form_valid(self, form):
        self.form = form
        incomplete_countries = models.CloudCommerceCountryID.incomplete.count()
        if incomplete_countries > 0:
            return redirect(reverse_lazy('spring_manifest:country_errors'))
        form.file_manifests()
        messages.add_message(
            self.request, messages.SUCCESS, 'Manifests Filed')
        for line in self.get_status_message():
            messages.add_message(self.request, messages.INFO, line)
        if self.form.download:
            messages.add_message(
                self.request, messages.INFO,
                self.get_download_message(self.form.download),
                extra_tags='hidden')
        return super().form_valid(form)


class CountryErrors(SpringUserMixin, FormView):
    template_name = 'spring_manifest/country_errors.html'
    form_class = forms.CloudCommerceCountryIDFormSet
    success_url = reverse_lazy('spring_manifest:spring_manifest')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = models.CloudCommerceCountryID.incomplete.all()
        return kwargs

    def form_valid(self, form):
        for country_form in form:
            country_form.save()
        return super().form_valid(form)


class DestinationZones(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/destination_zones.html'
