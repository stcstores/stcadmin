from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy

from . forms import NewSingleProductForm, NewVariationProductForm

from stcadmin import settings


def is_cloud_commerce_user(user):
    return user.groups.filter(name__in=['cloud_commerce'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def index(request):
    return render(request, 'cloud_commerce/index.html')


def new_product(request):
    return render(request, 'cloud_commerce/new_product.html')


class NewSingleProductView(FormView):
    template_name = 'cloud_commerce/new_product_form.html'
    form_class = NewSingleProductForm
    success_url = reverse_lazy('cloud_commerce:index')

    def form_valid(self, form):
        return super(NewSingleProductView, self).form_valid(form)


class NewVariationProductView(FormView):
    template_name = 'cloud_commerce/new_product_form.html'
    form_class = NewVariationProductForm
    success_url = reverse_lazy('cloud_commerce:index')

    def form_valid(self, form):
        return super(NewVariationProductView, self).form_valid(form)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def stock_manager(request):
    return render(request, 'cloud_commerce/stock_manager.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def sku_generator(request):
    return render(request, 'cloud_commerce/sku_generator.html')
