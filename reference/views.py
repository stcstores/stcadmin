from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'reference/index.html'


class SpringServices(LoginRequiredMixin, TemplateView):
    template_name = 'reference/spring_services.html'


class ProductCreation(LoginRequiredMixin, TemplateView):
    template_name = 'reference/product_creation_base.html'
