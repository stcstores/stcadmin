from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from home.views import UserInGroupMixin
from spring_manifest import models


class SpringUserMixin(UserInGroupMixin):
    groups = ['spring']


class Index(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/index.html'


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


class CanceledOrdersView(SpringUserMixin, TemplateView):
    template_name = 'spring_manifest/canceled_orders.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['unmanifested_orders'] = models.SpringOrder.unmanifested.all()
        context['canceled_orders'] = models.SpringOrder.canceled_orders.all()
        return context
