# -*- coding: utf-8 -*-
import json

from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet

from forms import VolunteerForm, UploadHomework, ActivityEvaluationForm
from models import Volunteer, VOLUNTEER_STATUS, ActivityDetail, EvaluationRule, ActivityEvaluation
from settings import LOGIN_URL, MEDIA_ROOT
import utils

VOLUNTEER_STATUS_DICT = utils.model_choice_2_dict(VOLUNTEER_STATUS)


@csrf_protect
@login_required(login_url=LOGIN_URL)
def user_home(request, user_id):
    data = {}
    user_id = request.user.id
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        data["message"] = "用户不存在"
        data["back_url"] = request.META["HTTP_REFERENCE"]
        return HttpResponseRedirect(utils.make_GET_url("/error/", data))

    volunteer_info = Volunteer.objects.filter(user_id=user_id)
    if volunteer_info :
        data["volunteer_status"] = volunteer_info[0].status

    return render_to_response("volunteer/user_home.html", data, context_instance=RequestContext(request))


@csrf_protect
@login_required(login_url=LOGIN_URL)
def volunteer_apply(request, user_id):
    # before register volunteer, the user must be the system's user
    template_name = "volunteer/apply_volunteer.html"
    data = {}
    if request.method == "GET":
        volunteer_model = Volunteer.objects.filter(user_id=user_id)
        if volunteer_model:
            data["volunteer_form"] = VolunteerForm(instance=volunteer_model[0])
        else:
            data["volunteer_form"] = VolunteerForm()
        return render_to_response(template_name, data,
                                  context_instance=RequestContext(request))
    else:  # POST
        volunteer_form = VolunteerForm(request.POST, request.FILES)
        if volunteer_form.is_valid():
            volunteer_model = Volunteer.objects.filter(user_id=user_id)
            if len(volunteer_model) > 0:
                data["message"] = "您的申请已修改。请等待管理员联系。 谢谢您的参与！"
                volunteer_model = VolunteerForm(instance=volunteer_model[0]).save(commit=False)
            else:
                data["message"] = "您的申请已递交，请等待管理员联系。 谢谢您的参与！"
                volunteer_model = volunteer_form.save(commit=False)

            if volunteer_form.cleaned_data.get("headshot"):
                utils.handle_upload_file(request.FILES["headshot"], "hs_" + user_id + ".jpeg", MEDIA_ROOT + '/headshot/')
                volunteer_model.headshot = "/media/headshot/" + "hs_" + user_id + ".jpeg"
            volunteer_model.free_time = request.POST.get("free_time")
            volunteer_model.user_id = user_id
            volunteer_model.status = '10'
            volunteer_model.volunteer_type = '01'

            volunteer_model.save()
            data["volunteer_form"] = volunteer_form

        else:
            data["volunteer_form"] = volunteer_form

        return render_to_response(template_name, data, context_instance=RequestContext(request))


@csrf_exempt
@login_required(login_url=LOGIN_URL)
def volunteer_status(request, user_id):
    data = {}
    volunteer_info = Volunteer.objects.filter(user_id=user_id)
    if volunteer_info:
        data[volunteer_info[0].status] = VOLUNTEER_STATUS_DICT.get(
            volunteer_info[0].status, volunteer_info[0].status)

    return HttpResponse(data.values())


@csrf_protect
@login_required(login_url=LOGIN_URL)
def volunteer_history(request):
    data = {}
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        data["message"] = "用户不存在"
        data["back_url"] = request.META["HTTP_REFERENCE"]
        return HttpResponseRedirect(utils.make_GET_url("/error/", data))

    volunteer_info = Volunteer.objects.get(user_id=user.id)
    if volunteer_info :
        data["volunteer_status"] = volunteer_info.status
    activity_as_speaker = ActivityDetail.objects.filter(
        speaker=volunteer_info.id
    )
    activity_as_assistant = ActivityDetail.objects.filter(
        assistant=volunteer_info.id
    )

    output = []
    for a in activity_as_speaker:
        output.append({
            'id': a.id,
            'role': 'speaker',
            'activity': a.activity,
            'date': a.activity_time.strftime("%Y-%m-%d"),
            'assistant': a.assistant,
            'status': a.status
        })

    for a in activity_as_assistant:
        output.append({
            'id': a.id,
            'role': 'assistant',
            'activity': a.activity,
            'date': a.activity_time.strftime("%Y-%m-%d") if a.activity_time else "",
            'speaker': a.speaker,
            'status': a.status
        })
    data["activity_history"] = output
    return render_to_response("volunteer/history.html", data, context_instance=RequestContext(request))


@csrf_protect
@login_required(login_url=LOGIN_URL)
def self_evaluation(request, activity_id):
    data = {}
    return HttpResponseRedirect('/volunteer/history/')


@csrf_protect
@login_required(login_url=LOGIN_URL)
def assistant_evaluation(request, activity_id):
    data = {}

    try:
        user = User.objects.get(id=request.user.id)
        vol = Volunteer.objects.get(user=user.id)
        if vol :
            data["volunteer_status"] = vol.status
    except User.DoesNotExist:
        data["message"] = "用户不存在"
        data["back_url"] = request.META["HTTP_REFERENCE"]

        return HttpResponseRedirect(utils.make_GET_url(data["back_url"], data))

    act = ActivityDetail.objects.filter(id=activity_id, assistant=vol.id)
    if not act:
        data["message"] = "没有该活动"

        return HttpResponseRedirect(utils.make_GET_url(data["back_url"], data))

    if request.method == 'GET':
        data['activity'] = act[0]
        evaluation_rules = EvaluationRule.objects.filter(evaluation_type=0)  # 课程相关评价规则
        data['evaluation_rules'] = [s for s in evaluation_rules]
        data['form'] = ActivityEvaluationForm()

        return render_to_response("volunteer/assistant_evaluation.html", data, context_instance=RequestContext(request))

    elif request.method == 'POST':
        act_detail_obj = ActivityDetail.objects.filter(id=request.POST.get('activity_detail_id', ''))
        if not act_detail_obj:
            return HttpResponseRedirect('/volunteer/history/')
        else:
            # todo next
            evaluation_obj = request.POST.get('evaluation_obj')
            eval_value = request.POST.get("value")
            # todo if evaluated then pass
            for eval in evaluation_obj:
                obj = EvaluationRule.objects.filter(id=eval)
                if not obj:
                    return HttpResponseRedirect('/volunteer/history/')
                ae = ActivityEvaluation()
                ae.activity = act_detail_obj
                # todo save new ae



    else:
        return HttpResponseRedirect('/volunteer/history/')


@csrf_protect
@login_required(login_url=LOGIN_URL)
def ask_for_leave(request, user_id):
    data = {}
    return render_to_response("volunteer/index.html", data, context_instance=RequestContext(request))


@csrf_protect
@login_required(login_url=LOGIN_URL)
def volunteer_homework(request, user_id):
    data = {}
    if request.method == "POST":
        upload_form = UploadHomework(request.POST, request.FILES)
        if upload_form.is_valid():
            # homework_name = user_id + upload_form.cleaned_data["homework_name"]
            # homework = Homework.objects.filter(owner=user_id, name=homework_name)
            # if homework:   # update
            #     homework.homework_file =
            # else:   # new
            #     homework = Homework(
            #         owner=user_id,
            #         name=homework_name)
            # homework.save()
            message = "上传成功"
        else:
            message = "上传失败"
        data["message"] = message
    homework_list = Homework.objects.filter(owner=user_id)
    data["homework"] = homework_list
    data["upload_form"] = UploadHomework()
    return render_to_response("volunteer/homework.html", data, context_instance=RequestContext(request))
