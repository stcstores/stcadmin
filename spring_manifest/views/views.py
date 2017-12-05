from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from home.views import UserInGroupMixin
from spring_manifest import forms, models


class SpringUserMixin(UserInGroupMixin):
    groups = ['spring']


class Index(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/index.html'


class UpdateOrderView(SpringUserMixin, FormView):
    form_class = forms.UpdateOrderForm
    fields = (
        'country', 'product_count', 'package_count', 'manifest', 'service')
    template_name = 'spring_manifest/update_order.html'

    def get_form_kwargs(self, *args, **kwargs):
        self.object = self.get_object()
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs['instance'] = self.object
        return form_kwargs

    def get_success_url(self):
        if 'split' in self.form.data:
            return reverse_lazy(
                'spring_manifest:split_order',
                kwargs={'order_pk': self.object.id})
        if 'return' in self.form.data:
            if self.object.manifest:
                return reverse_lazy(
                    'spring_manifest:manifest',
                    kwargs={'manifest_id': self.object.manifest_id})
            return reverse_lazy('spring_manifest:canceled_orders')
        return reverse_lazy(
            'spring_manifest:update_order',
            kwargs={'order_pk': self.object.id})

    def get_object(self):
        order = get_object_or_404(
            models.SpringOrder, id=self.kwargs.get('order_pk'))
        if order.manifest is not None:
            self.manifest_id = order.manifest.id
        else:
            self.manifest_id = None
        return order

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['order'] = self.object
        return context

    def form_valid(self, form):
        self.form = form
        form.save()
        if form.changed_data:
            messages.add_message(
                self.request, messages.SUCCESS, 'Order Updated.')
        return super().form_valid(form)


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
        models.update_spring_orders()
        manifest_id = self.kwargs['manifest_id']
        manifest = get_object_or_404(
            models.SpringManifest, id=manifest_id)
        orders = manifest.springorder_set.all().order_by('dispatch_date')
        context['manifest'] = manifest
        context['orders'] = orders
        return context


class CanceledOrdersView(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/canceled_orders.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['unmanifested_orders'] = models.SpringOrder.objects.filter(
            manifest__isnull=True, canceled=False)
        context['canceled_orders'] = models.SpringOrder.canceled_orders.filter(
            manifest__isnull=True, canceled=True)
        return context


class SplitOrderView(SpringUserMixin, FormView):
    form_class = forms.PackageFormset
    template_name = 'spring_manifest/split_order.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.order = get_object_or_404(
            models.SpringOrder, id=self.kwargs.get('order_pk'))
        kwargs['instance'] = self.order
        return kwargs

    def get_success_url(self):
        if 'return_to_order' in self.form.data:
            return reverse_lazy(
                'spring_manifest:update_order',
                kwargs={'order_pk': self.order.id})
        return reverse_lazy(
            'spring_manifest:split_order', kwargs={'order_pk': self.order.id})

    def form_valid(self, form):
        self.form = form
        form.save()
        form.clear_empty_packages()
        if 'add_package' in self.request.POST:
            form.add_package()
        if not self.order.check_items():
            messages.add_message(
                self.request, messages.WARNING, 'Item Quantity Discrepency.')
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['order'] = self.order
        context_data['children_formset'] = context_data.pop('form')
        return context_data
