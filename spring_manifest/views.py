from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from home.views import UserInGroupMixin
from spring_manifest import forms, models
from spring_manifest.forms import SpringManifestForm
from stcadmin import settings
import csv
from collections import OrderedDict
import datetime
import io
import xlsxwriter
from django.core.files import File


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


class UpdateOrderView(SpringUserMixin, UpdateView):
    model = models.SpringOrder
    fields = (
        'country', 'product_count', 'package_count', 'manifest', 'service',
        'canceled')
    template_name = 'spring_manifest/update_order.html'

    def get_success_url(self):
        if self.manifest_id is not None:
            return reverse_lazy(
                'spring_manifest:manifest',
                kwargs={'manifest_id': self.manifest_id})
        return reverse_lazy('spring_manifest:manifest_list')

    def get_object(self):
        order = get_object_or_404(self.model, id=self.kwargs.get('order_pk'))
        if order.manifest is not None:
            self.manifest_id = order.manifest.id
        else:
            self.manifest_id = None
        return order

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['order'] = self.object
        return context


class ManifestListView(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/manifest_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        models.update_spring_orders()
        context['current_manifests'] = models.SpringManifest.unfiled.all()
        context['previous_manifests'] = models.SpringManifest.filed.all()[:50]
        context['unmanifested_orders'] = models.SpringOrder.unmanifested.all()
        return context


class ManifestView(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/manifest.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        manifest_id = self.kwargs['manifest_id']
        manifest = get_object_or_404(
            models.SpringManifest, id=manifest_id)
        orders = manifest.springorder_set.all().order_by('dispatch_date')
        context['manifest'] = manifest
        context['orders'] = orders
        return context


class FileManifest(SpringUserMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        manifest_id = self.kwargs['manifest_id']
        manifest = get_object_or_404(
            models.SpringManifest, pk=manifest_id)
        if manifest.manifest_file:
            messages.add_message(
                self.request, messages.ERROR, 'Manifest already filed.')
        else:
            self.file_manifest(manifest)
        return reverse_lazy(
            'spring_manifest:manifest', kwargs={'manifest_id': manifest.id})

    def file_manifest(self, manifest):
        models.update_spring_orders()
        if manifest.manifest_type == manifest.TRACKED:
            self.file_tracked_manifest(manifest)
        elif manifest.manifest_type == manifest.UNTRACKED:
            self.file_untracked_manifest(manifest)

    def file_tracked_manifest(self, manifest):
        # TODO everything
        manifest.file_manifest()

    def file_untracked_manifest(self, manifest):
        self.zones = {}
        for order in manifest.springorder_set.all():
            zone = order.country.zone
            if zone not in self.zones:
                self.zones[zone] = []
            self.zones[zone].append(order)
        rows = [
            self.get_row_for_zone(zone, orders) for zone, orders in
            self.zones.items()]
        output = self.save_xlsx(manifest, rows)
        manifest.file_manifest()
        manifest.manifest_file.save(str(manifest) + '.xlsx', File(output))

    def save_xlsx(self, manifest, rows):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        for cell_number, col_header in enumerate(rows[0].keys()):
            worksheet.write(0, cell_number, col_header)
        for row_number, row in enumerate(rows, start=1):
            for col_number, cell in enumerate(row.values()):
                worksheet.write(row_number, col_number, cell)
        workbook.close()
        return output

    def save_csv(self, manifest, rows):
        output = io.StringIO(newline='')
        writer = csv.DictWriter(
            output, rows[0].keys(), delimiter=',', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
        return output

    def get_row_for_zone(self, zone, orders):
        customer_number = settings.SpringManifestSettings.customer_number
        products = []
        for order in orders:
            cc_order = order.get_order_data()
            products += cc_order.products
        weight_g = sum([
            product.per_item_weight * product.quantity for product in
            products])
        weight_kg = weight_g / 1000
        data = OrderedDict([
            ('CustomerNumber*', customer_number),
            ('Customer Reference 1', 'STC_STORES_{}_{}'.format(
                self.get_date_string(), zone.code)),
            ('Customer Reference 2', ''),
            ('PO Number', ''),
            ('Quote Reference', ''),
            ('Count items*', 'N'),
            ('Pre-franked*', 'N'),
            ('Product Code*', '1MI'),
            ('Nr satchels', '0'),
            ('Nr bags', len(self.zones)),
            ('Nr boxes', '0'),
            ('Nr pallets', '0'),
            ('Destination code*', zone.code),
            ('Format code', zone.format_code or ''),
            ('Weightbreak from', ''),
            ('Weightbreak to', ''),
            ('Nr items*', str(sum(order.package_count for order in orders))),
            ('Weight (kg)*', str(weight_kg)),
        ])
        return data

    def get_date_string(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')
