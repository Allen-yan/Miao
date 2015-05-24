# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from forms import VolunteerForm, CreationUserForm
from models import Volunteer, VOLUNTEER_STATUS
from settings import LOGIN_URL
import utils

VOLUNTEER_STATUS_DICT = utils.model_choice_2_dict(VOLUNTEER_STATUS)


def _get_current_username(request):
    if request.user.is_authenticated():
        return request.user
    else:
        return ""


def index(request):
    data = {
        "username": _get_current_username(request)
    }
    return render_to_response("volunteer/index.html", data, context_instance=RequestContext(request))


def error(request):
    data = {}
    for key in request.GET:
        data[key] = request.GET.get(key)

    return render_to_response("volunteer/error.html", data)


#=====================================================================
@csrf_protect
def register_user(request):
    if request.method == "GET":
        data = {
            "user_form": CreationUserForm()
        }
        return render_to_response("volunteer/register.html", data, context_instance=RequestContext(request))
    else:  # POST
        user_form = CreationUserForm(request.POST)
        data = {}
        if user_form.is_valid():
            new_user = User.objects.create_user(
                user_form.cleaned_data["username"],
                user_form.cleaned_data["email"],
                user_form.cleaned_data["password1"]
            )
            new_user.is_superuser = 0
            new_user.is_active = 1
            new_user.is_staff = 0
            new_user.save()
            data["message"] = "保存成功"
            data["username"] = new_user.username

            return HttpResponseRedirect("/volunteer/home/%s/" % new_user.id)
        else:
            data["user_form"] = user_form

            return render_to_response("volunteer/register.html", data, context_instance=RequestContext(request))


@csrf_protect
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)

                return HttpResponseRedirect("/volunteer/home/%s/" % user.id)
            else:
                data = {
                    "error_msg": "当前用户无法登陆"
                }
                return render_to_response('volunteer/login.html', data, context_instance=RequestContext(request))
        else:
            data = {
                "error_msg": "用户名称密码错误"
            }
            return render_to_response('volunteer/login.html', data, context_instance=RequestContext(request))
    else:
        # GET

        return render_to_response('volunteer/login.html', context_instance=RequestContext(request))


@csrf_protect
@login_required(login_url=LOGIN_URL)
def password_change_view(request):
    from django.contrib.auth.views import password_change

    return password_change(request, template_name="volunteer/change_password.html",
                           post_change_redirect="/account/password_change_done/")


def password_change_done(request):
    from django.contrib.auth.views import password_change_done

    return password_change_done(request, template_name='volunteer/change_password_done.html')


def logout(request):
    from django.contrib.auth import logout

    logout(request)

    return HttpResponseRedirect("/")
