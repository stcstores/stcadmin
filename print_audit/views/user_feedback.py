"""Views for User Feedback."""

from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from print_audit import forms, models

from .views import PrintAuditUserMixin


class FeedbackQuickview(TemplateView):
    """View for feedback quickview page."""

    template_name = 'print_audit/feedback_quickview.html'


class UserFeedback(PrintAuditUserMixin, TemplateView):
    """View for user feedback page."""

    template_name = 'print_audit/user_feedback.html'

    def get(self, *args, **kwargs):
        """Return blank form."""
        self.form = forms.FeedbackDateFilterForm(initial={'dates': 'all'})
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Process completed form."""
        self.form = forms.FeedbackDateFilterForm(self.request.POST)
        return super().get(*args, **kwargs)

    def get_context_data(self):
        """Return context data for template."""
        self.get_models()
        self.date_filter()
        self.get_pack_counts()
        self.get_feedback_counts()
        return {
            'users': self.users,
            'feedback_types': self.feedback_types,
            'feedback_counts': self.feedback_counts,
            'pack_counts': self.pack_counts,
            'form': self.form
        }

    def get_pack_counts(self):
        """Return dict of the number of order packed by users."""
        self.pack_counts = {
            user.id: self.orders.filter(user=user).count()
            for user in self.users
        }

    def get_feedback_counts(self):
        """Return dict of the number of feedbacks given to users."""
        self.feedback_counts = {}
        for user in self.users:
            self.feedback_counts[user.id] = {}
            for feedback_type in self.feedback_types:
                self.feedback_counts[user.id][
                    feedback_type.id] = self.feedback.filter(
                        user=user, feedback_type=feedback_type).count()

    def get_models(self):
        """Get users, feedback_types, orders and feedbacks."""
        self.users = sorted(
            models.CloudCommerceUser.unhidden.all(),
            key=lambda x: x.full_name())
        self.feedback_types = models.Feedback.objects.all()
        self.orders = models.CloudCommerceOrder.objects.all()
        self.feedback = models.UserFeedback.objects.all()

    def date_filter(self):
        """Filter search results by date."""
        if self.form.is_valid():
            if self.form.cleaned_data['date_from'] is not None:
                date_range = (
                    self.form.cleaned_data['date_from'],
                    self.form.cleaned_data['date_to'])
                self.orders = self.orders.filter(
                    date_created__gte=date_range[0],
                    date_created__lte=date_range[1])
                self.feedback = self.feedback.filter(
                    timestamp__gte=date_range[0], timestamp__lte=date_range[1])


class CreateUserFeedback(PrintAuditUserMixin, CreateView):
    """View for create user feedback page."""

    model = models.UserFeedback
    fields = ['user', 'timestamp', 'feedback_type', 'order_id', 'note']
    template_name = 'print_audit/user_feedback_form.html'
    success_url = reverse_lazy('print_audit:user_feedback')

    def get_initial(self):
        """Return initial values for form."""
        initial = super().get_initial()
        user_id = self.kwargs.get('user_id', None)
        if user_id is not None:
            initial['user'] = get_object_or_404(
                models.CloudCommerceUser, id=user_id)
        return initial

    def get_form(self, *args, **kwargs):
        """Add HTML class to the timestamp field."""
        form = super().get_form(*args, **kwargs)
        form.fields['timestamp'].widget.attrs['class'] = 'datepicker'
        return form


class UpdateUserFeedback(PrintAuditUserMixin, UpdateView):
    """View for update user feedback page."""

    model = models.UserFeedback
    fields = ['user', 'timestamp', 'feedback_type', 'order_id', 'note']
    template_name = 'print_audit/user_feedback_form.html'
    success_url = reverse_lazy('print_audit:user_feedback')

    def get_object(self):
        """Return UserFeedback object to update."""
        return get_object_or_404(self.model, id=self.kwargs.get('feedback_id'))

    def get_form(self, *args, **kwargs):
        """Add HTML class to the timestamp field."""
        form = super().get_form(*args, **kwargs)
        form.fields['timestamp'].widget.attrs['class'] = 'datepicker'
        return form


class DeleteUserFeedback(PrintAuditUserMixin, DeleteView):
    """View for deleting user feedback."""

    model = models.UserFeedback

    def get_success_url(self):
        """Return URL to redirect to after succesfull deletion."""
        return self.request.META.get('HTTP_REFERER')


class SafePaginator(Paginator):
    """Subclass paginator to handle invalid page numbers gracefully."""

    def validate_number(self, number):
        """
        Return valid page number.

        If requested page number is greater than the number of pages available
        return the last page number that is valid.
        """
        try:
            return super(SafePaginator, self).validate_number(number)
        except EmptyPage:
            if number > 1:
                return self.num_pages
            else:
                raise


class FeedbackList(PrintAuditUserMixin, ListView):
    """View for displaying user feedback."""

    paginator_class = SafePaginator
    template_name = 'print_audit/feedback_list.html'
    model = models.UserFeedback
    paginate_by = 50
    context_object_name = 'feedback_list'
    user = None
    feedback_type = None

    def get(self, *args, **kwargs):
        """Process GET request."""
        user_id = self.request.GET.get('user_id') or None
        if user_id is not None:
            self.user = get_object_or_404(models.CloudCommerceUser, pk=user_id)
        feedback_id = self.request.GET.get('feedback_id') or None
        if feedback_id is not None:
            self.feedback_type = get_object_or_404(
                models.Feedback, pk=feedback_id)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Process form data."""
        form = forms.FeedbackSearchForm(self.request.POST)
        if form.is_valid():
            self.user = form.cleaned_data.get('user') or None
            self.feedback_type = form.cleaned_data.get('feedback') or None
            self.paginate_by = form.cleaned_data.get(
                'paginate_by') or self.paginate_by
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Filter feedback according to form data."""
        queryset = self.model.objects.all()
        if self.user is not None:
            queryset = queryset.filter(user=self.user)
        if self.feedback_type is not None:
            queryset = queryset.filter(feedback_type=self.feedback_type)
        queryset = queryset.order_by('-timestamp')
        return queryset

    def get_initial(self):
        """Return initial data for form."""
        initial = {}
        if self.user is not None:
            initial['user'] = self.user.pk
        if self.feedback_type is not None:
            initial['feedback'] = self.feedback_type.pk
        initial['paginate_by'] = self.paginate_by
        return initial

    def get_context_data(self):
        """Return context data for template."""
        context = super().get_context_data()
        context['feedback_user'] = self.user
        context['feedback_type'] = self.feedback_type
        context['form'] = forms.FeedbackSearchForm(self.get_initial())
        return context


class FeedbackDetails(TemplateView):
    """View for feedback details page."""

    template_name = 'print_audit/feedback_details.html'

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        feedback_id = self.kwargs.get('feedback_id')
        context['feedback'] = get_object_or_404(
            models.UserFeedback, id=feedback_id)
        return context
