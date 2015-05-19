#-*- coding: UTF-8 -*-
from django.contrib import admin
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.encoding import force_text
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.utils.translation import ugettext, ugettext_lazy as _

from custom_model_admin import CustomModelAdmin
from apps.volunteer import models, choice
import db_utils


# ==================================================================
# =======================auth admin=================================
class SelfUserAdmin(UserAdmin):

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        if not obj:
            return self.add_fieldsets
        if not request.user.is_superuser:
            fieldsets = (
                    (None, {'fields': ('username', 'password')}),
                    (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                    (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
                )
        return fieldsets

    def get_queryset(self, request):
        qs = super(SelfUserAdmin, self).get_queryset(request)

        # only sys_admin and operator can edit auth's user info
        # If super-user, show all
        if request.user.is_superuser:
            return qs
        else:  # only operator
            vol_info = models.Volunteer.objects.get(user_id=request.user.id)
            if vol_info.level == '03':
                region_records = vol_info.operator_region.all()
                schools = []
                for r in region_records:
                    for s in r.schools.all():
                        schools.append(s.id)
                volunteer_groups = models.VolunteerGroup.objects.filter(school_for_work__in=schools)
                all_user_in_region = []
                for g in volunteer_groups:
                    for v in g.volunteers.all():
                        all_user_in_region.append(v.user.id)

                return qs.filter(id__in=all_user_in_region)
            else:
                return None

    # def get_form(self, request, obj=None, **kwargs):
    #     # if not request.user.is_superuser:
    #     #     return None
    #     return super(SelfUserAdmin, self).get_form(request, obj=None, **kwargs)
admin.site.unregister(User)
admin.site.register(User, SelfUserAdmin)

# ==================================================================
# =======================self admin=================================


class VolunteersAdmin(CustomModelAdmin):

    def sleep_volunteers(self, request, queryset):
        update_count = 0
        for vol in queryset:
            if vol.status >= '30':
                vol.status = '32'
                vol.save()
                update_count += 1
        self.message_user(request, "%s 志愿者状态变更为休眠." % update_count)
    sleep_volunteers.short_description = "休眠选中的志愿者"
    actions = [sleep_volunteers]

    list_display = ["name", "nick_name", "phone_number", "created_at", "status"]

    def get_queryset(self, request):
        qs = super(CustomModelAdmin, self).get_queryset(request)

        # If super-user, show all
        if request.user.is_superuser:
            return qs

        filter_dict = {}
        vol_info = models.Volunteer.objects.get(user_id=request.user.id)
        if vol_info.level == '02':   # group leader
            group_members = models.VolunteerGroup.objects.filter(
                group_leader_id=vol_info.id,
                status=1
            )
            if group_members:
                return group_members[0].volunteers
            else:
                return models.Volunteer.objects.none()
        elif vol_info.level == '03':
            # operator 所有未审核的 和 自己所管辖下的所有志愿者
            un_evaluate_vol = models.Volunteer.objects.filter(status='10')
            evaluated_vol = db_utils.get_operators_vols(vol_info.id)
            return un_evaluate_vol | evaluated_vol

        return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super(VolunteersAdmin, self).get_form(request, obj=None, **kwargs)
        if not request.user.is_superuser:
            vol_info = models.Volunteer.objects.get(user_id=request.user.id)
            # if vol_info.level == '01':   # normal volunteer
            #     pass
            # elif vol_info.level == '02':   # group leader
            #     self.exclude = ("level", "volunteer_type", "evaluation",
            #                     "evaluate_time", "training_time", "evaluation_of_training",
            #                     "homework", "free_time", )
            if vol_info.level == '03':  # group master
                form.base_fields["level"].choices = (
                    choice.VOLUNTEER_LEVEL[0], choice.VOLUNTEER_LEVEL[1]
                )
        else:
            form.base_fields["level"].choices = choice.VOLUNTEER_LEVEL
        return form

    fieldsets = (
        (u'名称', {
            'fields': ('name', 'phone_number')
        }),
        (u"基本信息", {
            'fields': ('nick_name', 'en_name', 'sex', 'age',
                       'wei_xin', 'weibo', 'is_in_school', 'graduated_school',
                       'education_background', 'profession', 'grade', 'forte',
                       'recent_company', 'job', 'working_years'),
            'classes': ('collapse ',)
        }),
        (u'志愿者申请信息', {
            'fields': ('why_in', 'want_to', 'self_introduction', 'volunteer_experience',
                       'reference', 'headshot'),
            'classes': ('collapse ',)
        }),
        (u'审核信息', {
            'fields': ('evaluation', 'evaluate_time'),
            'classes': ('collapse ',)
        }),
        (u'培训信息', {
            'fields': ('training_time', 'evaluation_of_training', 'homework'),
            'classes': ('collapse ',)
        }),
        (None, {
            'fields': ('status', 'level')
        })
    )

    group_leader_fieldsets = (fieldsets[0], fieldsets[1], fieldsets[5])

    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser:
            vol_info = models.Volunteer.objects.get(user_id=request.user.id)
            if vol_info.level == '02':   # group leader
                fieldsets = self.group_leader_fieldsets
            else:   # 03
                fieldsets = self.fieldsets
        else:
            fieldsets = [(None, {'fields': self.get_fields(request, obj)})]

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(CustomModelAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            vol_info = models.Volunteer.objects.get(user_id=request.user.id)
            if vol_info.level == '02':   # group leader
                fields = []
                for s in self.group_leader_fieldsets:
                    for f in s[1]["fields"]:
                        fields.append(f)
                readonly_fields = tuple(fields)
            elif vol_info.level == '03':
                readonly_fields = (None,)

        return readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            # update obj
            obj_old = self.model.objects.get(pk=obj.pk)
            modify_user = User.objects.get(id=obj.user_id)
            if obj_old.level != obj.level:
                db_utils.update_vol_type(obj, obj.level)
            if obj_old.eva_result != obj.eva_result:
                if obj.eva_result == '0':
                    modify_user.status = '20'
                else:
                    modify_user.status = '10'
            if obj_old.evaluation_of_training and modify_user.status >= '20':
                modify_user.status = '21'
            # todo next modify status

            modify_user.save()

            super(VolunteersAdmin, self).save_model(request, obj, form, change)
admin.site.register(models.Volunteer, VolunteersAdmin)


class VolunteerGroupAdmin(CustomModelAdmin):
    filter_horizontal = ('volunteers',)
    def get_queryset(self, request):
        qs = super(CustomModelAdmin, self).get_queryset(request).filter(status='1')
        if not request.user.is_superuser:
            vol_info = models.Volunteer.objects.get(user_id=request.user.id)
            if vol_info.level == '01':   # normal volunteer
                qs = None
            elif vol_info.level == '02':   # group leader
                qs = qs.filter(group_leader=vol_info.id)
            elif vol_info.level == '03':  # operator
                qs = qs.filter(school_for_work__in=db_utils.get_operators_schools(vol_info.id))

        return qs

    def save_model(self, request, obj, form, change):
        group_leader = obj.group_leader
        db_utils.update_vol_type(group_leader, '02')
        super(VolunteerGroupAdmin, self).save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super(VolunteerGroupAdmin, self).get_form(request, obj=None, **kwargs)
        if not request.user.is_superuser:
            vol_info = models.Volunteer.objects.get(user_id=request.user.id)
            if vol_info.level == '02':   # group leader
                region_schools = db_utils.get_group_leader_schools(vol_info)
            elif vol_info.level == '03':  # operator
                region_schools = db_utils.get_operators_schools(vol_info.id)
            form.base_fields["school_for_work"].queryset = region_schools

        return form
    list_display = ["group_name",]
admin.site.register(models.VolunteerGroup, VolunteerGroupAdmin)


class ClassesAdmin(CustomModelAdmin):
    list_display = ["class_name", "grade"]
admin.site.register(models.Class, ClassesAdmin)


class CoursesAdmin(CustomModelAdmin):
    list_display = ["name", "book"]
admin.site.register(models.Course, CoursesAdmin)


class SchoolAdmin(CustomModelAdmin):
    list_display = ["school_name", "description"]
admin.site.register(models.School, SchoolAdmin)


class ActivityPublishAdmin(CustomModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        form = super(ActivityPublishAdmin, self).get_form(request, obj=None, **kwargs)
        # 仅有申请第一/第二志愿的志愿者才能被选中
        if obj:
            form.base_fields["confirm_volunteers"].queryset = \
                (obj.apply_volunteers.all() | obj.apply_volunteers2.all()).distinct()

        return form
    def response_change(self, request, obj):
        if "_continue" in request.POST:
            # when user click the '_continue' button which is confirm button in this model
            if obj.status == 1:
                obj.status = 2
                obj.save()

                # 将所选组长志愿者 的类型变更
                db_utils.update_vol_type(obj.group_leader, '02')

        return super(ActivityPublishAdmin, self).response_change(request, obj)


    def save_model(self, request, obj, form, change):
        obj.status = 1
        super(ActivityPublishAdmin, self).save_model(request, obj, form, change)

    filter_horizontal = ("confirm_volunteers", )
    readonly_fields = ("status", "apply_volunteers", "apply_volunteers2")
    list_display = ["activity_name", "group_leader", "course", "class_id", "activity_type", "status"]
admin.site.register(models.ActivityPublish, ActivityPublishAdmin)


class ActivityDetailAdmin(CustomModelAdmin):
    list_display = ["activity", "activity_time", "speaker", "assistant"]
    filter_horizontal = ("speaker_self", )
    readonly_fields = ['status', 'assistant_2_speaker', 'meta']

    def get_form(self, request, obj=None, **kwargs):
        form = super(ActivityDetailAdmin, self).get_form(request, obj=None, **kwargs)


        if obj:
            form.base_fields["speaker"].queryset = obj.activity.confirm_volunteers.all()
            form.base_fields["assistant"].queryset = obj.activity.confirm_volunteers.all()
        else:
            form.base_fields["speaker"].queryset = form.base_fields["assistant"].queryset = models.Volunteer.objects.\
                filter(volunteer_type='01',status_gte='31')
        # todo next activity flow
        if not request.user.is_superuser:
            vol_info = models.Volunteer.objects.get(user_id=request.user.id)
            if vol_info.level == '01':   # normal volunteer
                form = None
            elif vol_info.level == '02':   # group leader
                form.base_fields["activity"].queryset = models.ActivityPublish.objects.filter(
                    status=2,
                    group_leader=vol_info)
            elif vol_info.level == '03':  # operator
                form.base_fields["activity"].queryset = models.ActivityPublish.objects.filter(
                    status=2,
                    group_leader=vol_info)
            else:
                form.base_fields["activity"].queryset = models.ActivityPublish.objects.all()

        return form
admin.site.register(models.ActivityDetail, ActivityDetailAdmin)


class CheckInAdmin(CustomModelAdmin):
    list_display = ["volunteer", "created_at"]
admin.site.register(models.CheckIn, CheckInAdmin)


class BookAdmin(CustomModelAdmin):
    list_display = ["owner_school", "name", "auth", "description"]
admin.site.register(models.Book, BookAdmin)


# class EvaluationAdmin(CustomModelAdmin):
#     list_display = ["evaluation_value"]
# admin.site.register(models.Evaluation, EvaluationAdmin)


class EvaluationRuleAdmin(CustomModelAdmin):
    list_display = ["item"]
admin.site.register(models.EvaluationRule, EvaluationRuleAdmin)


class OperatorRegionAdmin(CustomModelAdmin):
    list_display = ["operator", "status"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(OperatorRegionAdmin, self).get_form(request, obj=None, **kwargs)
        form.base_fields["operator"].queryset = models.Volunteer.objects.filter(level="03")

        return form

admin.site.register(models.OperatorRegion, OperatorRegionAdmin)