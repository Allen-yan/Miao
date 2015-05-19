#-*- coding: UTF-8 -*-
import models
from django.contrib.auth.models import User, Group

def get_operators_schools(volunteer_id):
    regions = models.OperatorRegion.objects.filter(operator=volunteer_id)
    schools_in_region = models.OperatorRegion.objects.none()
    for region in regions:
        # 取所有集合的或集
        schools_in_region |= region.schools.all()

    return schools_in_region

def get_operators_vol_group(volunteer_id):
    schools = get_operators_schools(volunteer_id)
    vol_groups_in_schools = models.VolunteerGroup.objects.none()
    for school in schools:
        groups = models.VolunteerGroup.objects.filter(school_for_work=school.id)
        vol_groups_in_schools |= groups

    return vol_groups_in_schools

def get_operators_vols(volunteer_id):
    groups = get_operators_vol_group(volunteer_id)
    vols = models.Volunteer.objects.none()
    for g in groups:
        vols |= g.volunteers.all()

    return vols

def get_group_leader_schools(vol_obj):
    schools = models.School.objects.none()
    groups = models.VolunteerGroup.objects.filter(group_leader=vol_obj)
    for group in groups:
        schools |= models.School.objects.filter(id=group.school_for_work.id)

    return schools

def get_vol_schools(vol_obj):
    result = {}
    groups = vol_obj.volunteer_groups.all()
    for group in groups:
        result[group.school_for_work.id] = ""
    return result.keys()


def update_vol_type(vol_obj, new_type):
    obj_user = vol_obj.user   # auth user
    vol_obj.level = new_type
    obj_user.groups.clear()
    if new_type == '04':   # admin
        obj_user.is_staff = True
        obj_user.is_superuser = True
        operator_group = Group.objects.get(name=u"系统管理员")
        obj_user.groups.add(operator_group)
    elif new_type == '02':   # group leader
        obj_user.is_staff = True
        obj_user.is_superuser = False
        operator_group = Group.objects.get(name=u"组长")
        obj_user.groups.add(operator_group)
    elif new_type == '03':  # operator
        obj_user.is_staff = True
        obj_user.is_superuser = False
        operator_group = Group.objects.get(name=u"运营")
        obj_user.groups.add(operator_group)
    else:    # normal vol
        obj_user.is_staff = False
        obj_user.is_superuser = False

    obj_user.save()
    vol_obj.save()

