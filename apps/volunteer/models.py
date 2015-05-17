# -*- encoding:utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from choice import *


class BaseModelMixin(models.Model):
    created_at = models.DateTimeField(u"时间", null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    # 0-deleted, 1-normal, ...
    status = models.IntegerField(verbose_name="状态", default="1", choices=STATUS)

    # Abstract class . Will not generate a table
    class Meta:
        abstract = True


class School(BaseModelMixin):
    id = models.AutoField(primary_key=True)
    school_name = models.CharField(u"学校名称", max_length=50)
    description = models.CharField(u"描述", max_length=50, null=True, blank=True)
    schoolmaster = models.CharField(u"校长", max_length=50)
    schoolmaster_phone = models.CharField(u"校长联系方式", max_length=50)
    address = models.CharField(u"地址", max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = u"学校"
        verbose_name_plural = u"学校"
        permissions = (
            ("view_only_school",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return self.school_name


class Volunteer(models.Model):
    created_at = models.DateTimeField(u"申请时间", auto_now_add=True)
    updated_at = models.DateTimeField(u"更新时间", null=True, blank=True, auto_now=True)
    user = models.OneToOneField(User, verbose_name="关联系统账号", related_name="volunteer_account")
    volunteer_type = models.CharField(u"志愿者类别", max_length=2, default='01', choices=VOLUNTEER_TYPE)
    level = models.CharField(u"级别", max_length=2, choices=VOLUNTEER_LEVEL, default='01')
    name = models.CharField(u"真实名称", max_length=50)
    nick_name = models.CharField(u"昵称", max_length=50, null=True, blank=True)
    en_name = models.CharField(u"英文名称", max_length=50, null=True, blank=True)
    sex = models.CharField(u"性别", max_length=1, choices=SEX_CHOICE)
    age = models.IntegerField(u"年龄", null=True, blank=True)
    phone_number = models.CharField(u"联系方式", max_length=50)
    wei_xin = models.CharField(u"微信账号", max_length=50, null=True, blank=True)
    weibo = models.CharField(u"微博帐号", max_length=50, null=True, blank=True)
    # ---------------------------education background
    is_in_school = models.BooleanField(u"是否在校", default=False)
    graduated_school = models.CharField(u"毕业院校", max_length=50, null=True, blank=True)
    education_background = models.CharField(u"最高学历", max_length=50, null=True, blank=True)
    profession = models.CharField(u"专业", max_length=50, null=True, blank=True)
    grade = models.CharField(u"年级(在校学生)", max_length=50, null=True, blank=True)
    # ---------------------------working experience
    forte = models.CharField(u"特长", max_length=100, null=True, blank=True)
    recent_company = models.CharField(u"最近就职公司", max_length=50, null=True, blank=True)
    job = models.CharField(u"最近担任职务", max_length=50, null=True, blank=True)
    working_years = models.IntegerField(u"工作年限", null=True, blank=True)

    why_in = models.TextField(u"为什么想加入", )
    want_to = models.TextField(u"想从中获得", )

    self_introduction = models.TextField(u"自我介绍", )
    volunteer_experience = models.TextField(u"志愿者服务经验", null=True, blank=True)
    reference = models.CharField(u"推荐人", max_length=20, null=True, blank=True)
    headshot = models.FileField(u"大头照", upload_to="headshot/", null=True, blank=True)
    #=============================================================
    # 志愿者审核阶段
    evaluation = models.TextField(u"审核评价", null=True, blank=True)
    eva_result = models.CharField(u"审核是否通过", choices=YES_NO, default='0', max_length=1)
    evaluate_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    #=============================================================
    # 培训活动
    training_time = models.DateTimeField(u'培训时间', null=True, blank=True)
    evaluation_of_training = models.TextField(u"培训评价", null=True, blank=True)
    #=============================================================
    # 作业
    homework = models.FileField(u"作业文件", upload_to="homework/", null=True, blank=True)

    free_time = models.TextField(u"空闲时间", null=True, blank=True)

    status = models.CharField(u"状态", max_length='2', choices=VOLUNTEER_STATUS)

    class Meta:
        verbose_name = u"志愿者"
        verbose_name_plural = u"志愿者"
        permissions = (
            ("view_only_volunteer",  u"可以查看%s相关信息" % verbose_name),
        )
    def __unicode__(self):
        return self.name


class VolunteerGroup(BaseModelMixin):
    group_name = models.CharField(u"小组名称", max_length=50, unique=True)
    school_for_work = models.ForeignKey(to=School, verbose_name="服务学校")
    group_leader = models.ForeignKey(Volunteer, verbose_name="组长", related_name="group_leader")
    effective_year = models.CharField(u"有效期--年", max_length=4, choices=YEARS)
    effective_season = models.CharField(u"有效期--季度", max_length=1, choices=SEASON)
    volunteers = models.ManyToManyField(Volunteer, related_name="volunteer_groups")

    class Meta:
        verbose_name = u"志愿者小组"
        verbose_name_plural = u"志愿者小组"
        db_table = "volunteer_group"
        permissions = (
            ("view_only_volunteer_group",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return self.group_name

    def clean(self):
        # select a volunteer to the group's leader
        if self.group_leader.level not in ['01', '02']:
            raise ValidationError(u"志愿者%s不能被选为组长！" % self.group_leader.name)


class OperatorRegion(BaseModelMixin):
    operator = models.ForeignKey(to=Volunteer, verbose_name="运营管理员", related_name="operator_region")
    schools = models.ManyToManyField(School, related_name="schools_in_region")

    class Meta:
        verbose_name = u"运营管理范围"
        verbose_name_plural = u"运营管理范围"

    def __unicode__(self):
        return self.operator.name

class CheckIn(BaseModelMixin):
    volunteer = models.ForeignKey(Volunteer, related_name="volunteers", verbose_name="志愿者")
    check_in_date = models.DateTimeField(u"签到时间", null=True, blank=True)

    class Meta:
        verbose_name = u"签到"
        verbose_name_plural = u"签到"
        permissions = (
            ("view_only_checkin",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return unicode(self.volunteer)


class Book(BaseModelMixin):
    owner_school = models.ForeignKey(School, verbose_name="所属学校")
    name = models.CharField(u"书名", max_length=50)
    auth = models.CharField(u"作者", max_length=50, null=True, blank=True)
    description = models.TextField(u"简介", null=True, blank=True)

    class Meta:
        verbose_name = u"书"
        verbose_name_plural = u"书"
        permissions = (
            ("view_only_book",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return self.name


class Class(BaseModelMixin):
    class_name = models.CharField(u"班级", max_length=50)
    grade = models.CharField(u"年级", max_length=50)
    contact = models.CharField(u"联系人", max_length=50, null=True, blank=True)
    school = models.ForeignKey(School, verbose_name="学校")
    student_count = models.IntegerField(u"学生人数", null=True, blank=True)

    class Meta:
        verbose_name = u"班级"
        verbose_name_plural = u"班级"
        permissions = (
            ("view_only_class",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return u"%s:%s年级 %s班" % (self.school, self.grade, self.class_name)


class Course(BaseModelMixin):
    name = models.CharField(u"课程名称", max_length=50)
    book = models.ForeignKey(Book, verbose_name="书")
    designer = models.CharField(u"课程设计者", max_length=50, null=True, blank=True)
    description = models.TextField(u"描述", null=True, blank=True)

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = u"课程"
        permissions = (
            ("view_only_course",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return self.name


class EvaluationRule(BaseModelMixin):
    item = models.CharField(u"评价项目", max_length=50)
    description = models.CharField(u"描述", max_length=50, null=True, blank=True)
    evaluation_type = models.IntegerField(u"类型", default=0, choices=EVALUATION_TYPE, null=True, blank=True)

    class Meta:
        verbose_name = u"评价规则"
        verbose_name_plural = u"评价规则"
        permissions = (
            ("view_only_evaluation_rule",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return self.item


class Evaluation(BaseModelMixin):
    evaluation_rule = models.ForeignKey(EvaluationRule, verbose_name="评价规则")
    evaluation_value = models.IntegerField(u"评价", default="2", choices=EVALUATION)

    class Meta:
        verbose_name = u"评价"
        verbose_name_plural = u"评价"
        permissions = (
            ("view_only_evaluation",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return "%s: %s" % (self.evaluation_rule.item, self.evaluation_value)


class ActivityPublish(models.Model):
    activity_name = models.CharField(u"名称", max_length=100)
    effective_year = models.CharField(u"活动时间-年", max_length=4, choices=YEARS)
    effective_season = models.CharField(u"活动时间-季度", max_length=1, choices=SEASON)
    class_time = models.CharField(u"活动时间", max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(u"发布时间", null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(u"更新时间", null=True, blank=True, auto_now=True)
    group_leader = models.ForeignKey(Volunteer, verbose_name="组长", related_name="activity_group_leader")
    course = models.ForeignKey(Course, verbose_name="课程")
    class_id = models.ForeignKey(Class, verbose_name="班级")
    activity_type = models.IntegerField(u"活动形式", default=0, choices=ACTIVITY_TYPE)
    status = models.IntegerField(u"状态", default=0, choices=COURSE_STATUS)
    apply_volunteers = models.ManyToManyField(
        Volunteer, verbose_name=u"第一志愿", related_name="vol1", null=True, blank=True)
    apply_volunteers2 = models.ManyToManyField(
        Volunteer, verbose_name=u"第二志愿", related_name="vol2", null=True, blank=True)
    confirm_volunteers = models.ManyToManyField(
        Volunteer, verbose_name=u"确认志愿者", related_name="con_vol", null=True, blank=True)

    class Meta:
        verbose_name = u"活动发布"
        verbose_name_plural = u"活动发布"
        permissions = (
            ("view_only_activity_publish",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return "%s-%s:%s" % (self.effective_year, self.effective_season, self.activity_name)


class ActivityDetail(models.Model):
    # all activity details are created by group leaders
    activity = models.ForeignKey(ActivityPublish, verbose_name="活动主题")
    activity_time = models.DateTimeField(u"上课时间", null=True, blank=True)
    speaker = models.ForeignKey(Volunteer, verbose_name="主讲", related_name="speakser")
    assistant = models.ForeignKey(Volunteer, verbose_name="助理", related_name="assistant", null=True, blank=True)
    assistant_2_speaker = models.TextField(u"助理评主讲", null=True, blank=True)
    # speaker_self = models.TextField(u"主讲自评", null=True, blank=True)
    speaker_self = models.ManyToManyField(Evaluation, verbose_name=u"主讲自评", null=True, blank=True)
    meta = models.TextField(u"其它信息", null=True, blank=True)
    status = models.IntegerField(u"状态", default=0, choices=COURSE_STATUS)

    class Meta:
        verbose_name = u"活动详情"
        verbose_name_plural = u"活动详情"
        permissions = (
            ("view_only_activity_detail",  u"可以查看%s相关信息" % verbose_name),
        )

    def __unicode__(self):
        return self.activity.activity_name

class AskForLeave(models.Model):
    id = models.AutoField(u"id", primary_key=True)
    volunteer = models.ForeignKey(Volunteer)
    activity = models.ForeignKey(ActivityDetail, verbose_name=u"请假活动")
    created_at = models.DateTimeField(u"请假时间", auto_created=True)
    status = models.CharField(u"状态", max_length=1, choices=ASK_FOR_LEAVE_STATUS, default='0')

    class Meta:
        verbose_name = u"请假"
        verbose_name_plural = u"请假"

    def __unicode__(self):
        return u"%s请假" % self.volunteer