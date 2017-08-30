from stcadmin import settings
from django.shortcuts import render
from django.contrib.auth.views import password_change
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from print_audit import models

@login_required(login_url=settings.LOGIN_URL)
def user(request):
    try:
        user = models.CloudCommerceUser.objects.filter(stcadmin_user=request.user)[0]
    except Exception as e:
        raise
    feedback_types = models.Feedback.objects.all()
    feedback_count = {feedback_type: models.UserFeedback.objects.filter(user=user.pk, feedback_type=feedback_type).count() for feedback_type in feedback_types}
    return render(request, 'user/user.html', {'feedback_count': feedback_count})


@login_required(login_url=settings.LOGIN_URL)
def change_password(request):
    return password_change(request, 'user/change_password.html')


def change_password_done(request):
    logout(request)
    return render(request, 'user/change_password_done.html')
