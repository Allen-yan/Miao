# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from forms import ActivityPublicForm
from models import ActivityPublish, VOLUNTEER_STATUS, Volunteer
from settings import LOGIN_URL
import utils

VOLUNTEER_STATUS_DICT = utils.model_choice_2_dict(VOLUNTEER_STATUS)


#=====================================================================
@csrf_protect
@login_required(login_url=LOGIN_URL)
def list_activity(request):
    data = {}
    template_name = "volunteer/activity_list.html"
    activities = ActivityPublish.objects.filter(status__in=[1, 2])
    activity_form = ActivityPublicForm()

    if not request.user.is_anonymous():
        volunteer_info = Volunteer.objects.filter(user_id=request.user.id)
        if volunteer_info :
            data["volunteer_status"] = volunteer_info[0].status
    data["activities"] = activities
    data["activity_form"] = activity_form

    return render_to_response(template_name, data, context_instance=RequestContext(request))


@csrf_protect
@login_required(login_url=LOGIN_URL)
def application(request, choice, user_id, activity_id):
    vol = Volunteer.objects.filter(user=user_id, status__gte='30')
    if str(request.user.id) != user_id or not vol:
        message = "不合法申请用户。"
    else:
        vol = vol[0]
        selected_activity = ActivityPublish.objects.filter(id=activity_id, status=1)
        if not selected_activity:
            message = "无法申请该活动。"
        else:
            selected_activity = selected_activity[0]
            if choice == 'first':
                if vol in selected_activity.apply_volunteers.all():
                    message = "您已在该活动的第一志愿列表中。"
                else:
                    selected_activity.apply_volunteers.add(vol)
                    message = "第一志愿申请成功"
            else:    # second
                if vol in selected_activity.apply_volunteers2.all():
                    message = "您已在该活动的第二志愿列表中。"
                else:
                    selected_activity.apply_volunteers2.add(vol)
                    message = "第二志愿申请成功"
            #  成为活跃志愿者
            vol.status = '31'
            selected_activity.save()

    return HttpResponseRedirect("/activities/?message=%s" % message)


@csrf_protect
@login_required(login_url=LOGIN_URL)
def cancel_application(request, choice, user_id, activity_id):
    vol = Volunteer.objects.filter(user=user_id, status__gte='30')
    if str(request.user.id) != user_id  or not vol:
        message = "不合法申请用户。"
    else:
        vol = vol[0]
        selected_activity = ActivityPublish.objects.filter(id=activity_id, status=1)
        if not selected_activity:
            message = "无法撤销该活动。"
        else:
            selected_activity = selected_activity[0]
            if choice == 'first':
                if vol not in selected_activity.apply_volunteers.all():
                    message = "您不在该活动的第一志愿列表中，无法撤销。"
                else:
                    selected_activity.apply_volunteers.remove(vol)
                    message = "第一志愿撤销成功"
            else:    # second
                if vol not in selected_activity.apply_volunteers2.all():
                    message = "您不在该活动的第二志愿列表中， 无法撤销"
                else:
                    selected_activity.apply_volunteers2.remove(vol)
                    message = "第二志愿撤销成功"
            selected_activity.save()

    return HttpResponseRedirect("/activities/?message=%s" % message)
