from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'reference/index.html'


class SpringServices(LoginRequiredMixin, TemplateView):
    template_name = 'reference/spring_services.html'


class ReStructuredTextView(TemplateView):
    rst_file = None
    template_name = 'reference/rst_base.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rst_file'] = self.rst_file
        return context


class ProductCreation(LoginRequiredMixin, ReStructuredTextView):
    rst_file = 'reference/product_creation.rst'
