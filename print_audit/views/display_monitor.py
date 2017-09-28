import json

from django.http import HttpResponse
from django.utils.timezone import now
from django.views import View
from django.views.generic.base import TemplateView
from print_audit import models


class DisplayMonitor(TemplateView):
    template_name = 'print_audit/display_monitor.html'


class PackCountMonitor(View):

    def get(self, request):
        orders = models.CloudCommerceOrder.objects.filter(
            date_created__year=now().year,
            date_created__month=now().month,
            date_created__day=now().day)
        packers = models.CloudCommerceUser.objects.all()
        pack_count = [
            (user.full_name(), orders.filter(user=user).count())
            for user in packers]
        pack_count = [
            count for count in pack_count if count[1] > 0]
        pack_count.sort(key=lambda x: x[1], reverse=True)
        return HttpResponse(json.dumps(pack_count))


class FeedbackMonitor(View):

    def get(self, request):
        feedback_types = models.Feedback.objects.order_by('score')
        users = models.CloudCommerceUser.objects.all()
        data = []
        for user in users:
            counts = {}
            for f in feedback_types:
                count = models.UserFeedback.objects.filter(
                    user=user, feedback_type=f,
                    timestamp__month=now().month).count()
                counts[f.pk] = count
            if max(set(counts.values())) == 0:
                continue
            user_data = {'name': user.full_name(), 'feedback': []}
            for f in feedback_types:
                count = counts[f.pk]
                user_data['feedback'].append({
                    'name': f.name, 'image_url': f.image.url, 'count': count,
                    'score': f.score})
            user_data['score'] = sum(
                [d['score'] * d['count'] for d in user_data['feedback']])
            data.append(user_data)
        data.sort(key=lambda x: x['score'], reverse=True)
        return HttpResponse(json.dumps(data))
