from django.views.generic.base import TemplateView


class Index(TemplateView):
    template_name = 'reference/index.html'


class SpringServices(TemplateView):
    template_name = 'reference/spring_services.html'
