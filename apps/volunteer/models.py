# -*- encoding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

SEX_CHOICE = (
    ("M", u"男"),
    ("F", u"女")
)

USER_LEVEL = (
    (0, u"管理员"),
    (1, u"普通用户")
)


STATUS = (
    (0, u"禁用"),
    (1, u"正常"),
)


VOLUNTEER_STATUS = (
    (0, u"申请中"),
    (1, u"审核中"),
    (2, u"正常"),
    (3, u"注销"),
)


class BaseModel(models.Model):
    created_at = models.DateTimeField(u"时间", null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    # 0-deleted, 1-normal, ...
    status = models.IntegerField(verbose_name="状态", default="1", choices=STATUS)

    # Abstract class . Will not generate a table
    class Meta:
        abstract = True


class Volunteer(models.Model):
    user = models.OneToOneField(User, verbose_name="账号")
    name = models.CharField(u"真实名称", max_length=50)
    nick_name = models.CharField(u"昵称", max_length=50, null=True, blank=True)
    en_name = models.CharField(u"英文名称", max_length=50, null=True, blank=True)
    sex = models.CharField(u"性别", max_length=1, choices=SEX_CHOICE)
    age = models.IntegerField(u"年龄", null=True, blank=True)
    phone_number = models.CharField(u"联系方式", max_length=50)
    is_in_school = models.BooleanField(u"是否在校", default=False)
    email = models.EmailField(u"邮箱", max_length=50, null=True, blank=True)
    wei_xin = models.CharField(u"微信账号", max_length=50, null=True, blank=True)
    weibo = models.CharField(u"微博帐号", max_length=50, null=True, blank=True)
    # ---------------------------education background
    xueli = models.CharField(u"最高学历", max_length=50, null=True, blank=True)
    profession = models.CharField(u"专业", max_length=50, null=True, blank=True)
    grade = models.CharField(u"年级(在校学生)", max_length=50, null=True, blank=True)
    # ---------------------------working experience
    forte = models.CharField(u"特长", max_length=100, null=True, blank=True)
    recent_company = models.CharField(u"最近就职公司", max_length=50, null=True, blank=True)
    job = models.CharField(u"最近担任职务", max_length=50, null=True, blank=True)
    working_years = models.IntegerField(u"工作年限", null=True, blank=True)

    self_introduction = models.TextField(u"自我介绍", null=True, blank=True)
    volunteer_experience = models.TextField(u"志愿者工作经验", null=True, blank=True)

    free_time = models.TextField(u"空闲时间", null=True, blank=True)

    status = models.IntegerField(u"状态", default=0, choices=VOLUNTEER_STATUS, null=True, blank=True)

    class Meta:
        verbose_name = u"志愿者"
        verbose_name_plural = u"志愿者"

    def __unicode__(self):
        return self.name


class Group(BaseModel):
    group_name = models.CharField(u"小组名称", max_length=50, unique=True)

    class Meta:
        verbose_name = u"志愿者小组"
        verbose_name_plural = u"志愿者小组"

    def __unicode__(self):
        return self.account


class CheckIn(BaseModel):
    volunteer = models.ForeignKey(Volunteer, related_name="volunteers", verbose_name="志愿者")
    check_in_date = models.DateTimeField(u"签到时间", null=True, blank=True)

    class Meta:
        verbose_name = u"签到"
        verbose_name_plural = u"签到"

    def __unicode__(self):
        return unicode(self.volunteer)


class Book(models.Model):
    name = models.CharField(u"书名", max_length=50)
    auth = models.CharField(u"作者", max_length=50, null=True, blank=True)
    description = models.TextField(u"简介", null=True, blank=True)

    class Meta:
        verbose_name = u"书"
        verbose_name_plural = u"书"

    def __unicode__(self):
        return self.name


class School(BaseModel):
    id = models.AutoField(primary_key=True)
    school_name = models.CharField(u"学校名称", max_length=50)
    description = models.CharField(u"描述", max_length=50, null=True, blank=True)
    contact = models.CharField(u"联系人", max_length=50, null=True, blank=True)
    address = models.CharField(u"地址", max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = u"学校"
        verbose_name_plural = u"学校"

    def __unicode__(self):
        return self.school_name


class Class(BaseModel):
    class_name = models.CharField(u"班级", max_length=50)
    grade = models.CharField(u"年级", max_length=50)
    contact = models.CharField(u"联系人", max_length=50, null=True, blank=True)
    school = models.ForeignKey(School, verbose_name="学校")
    student_count = models.IntegerField(u"学生人数", null=True, blank=True)

    class Meta:
        verbose_name = u"班级"
        verbose_name_plural = u"班级"

    def __unicode__(self):
        return u"%s年级 %s班" % (self.grade, self.class_name)


class Course(BaseModel):
    name = models.CharField(u"课程名称", max_length=50)
    book = models.ForeignKey(Book, verbose_name="书")
    designer = models.ForeignKey(Volunteer, verbose_name="课程设计者")
    description = models.TextField(u"描述", null=True, blank=True)

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = u"课程"

    def __unicode__(self):
        return self.name


EVALUATION_TYPE = (
    (0, u"课程"),
    (1, u"志愿者"),
    (2, u"书籍"),
    (3, u"活动"),
    (9, u"其他")
)


class EvaluationRule(models.Model):
    item = models.CharField(u"评价项目", max_length=50)
    description = models.CharField(u"描述", max_length=50, null=True, blank=True)
    evaluation_type = models.IntegerField(u"类型", default=0, choices=EVALUATION_TYPE, null=True, blank=True)

    class Meta:
        verbose_name = u"评价规则"
        verbose_name_plural = u"评价规则"

    def __unicode__(self):
        return self.item


EVALUATION = (
    (0, u"非常同意"),
    (1, u"同意"),
    (2, u"一般"),
    (3, u"不同意"),
    (4, u"非常不同意")
)


class Evaluation(models.Model):
    evaluation_rule = models.ForeignKey(EvaluationRule, verbose_name="评价规则")
    evaluation_value = models.IntegerField(u"评价", default="2", choices=EVALUATION)

    class Meta:
        verbose_name = u"评价"
        verbose_name_plural = u"评价"

    def __unicode__(self):
        return "%s: %s" % (self.evaluation_rule.item, self.evaluation_value)


COURSE_STATUS = (
    (0, u"未开始"),
    (1, u"未评估"),
    (2, u"已评估"),
)

ACTIVITY_TYPE = (
    (0, u"阅读"),
    (1, u"伴读"),
    (9, u"其他")
)


class Activity(models.Model):
    created_at = models.DateTimeField(u"时间", null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    course = models.ForeignKey(Course, verbose_name="课程")
    class_id = models.ForeignKey(Class, verbose_name="班级")
    volunteer = models.ManyToManyField(Volunteer, related_name="volunteer", verbose_name="志愿者")
    assistant = models.ForeignKey(Volunteer, related_name="assistant", verbose_name="助教")
    class_time = models.DateTimeField(u"上课时间", null=True, blank=True)
    status = models.IntegerField(u"状态", default="0", choices=COURSE_STATUS)
    class_evaluation = models.ManyToManyField(Evaluation, verbose_name="评价", null=True, blank=True)

    address = models.CharField(u"地址", max_length=100, null=True, blank=True)

    activity_type = models.IntegerField(u"活动类型", default=0, choices=ACTIVITY_TYPE)

    class Meta:
        verbose_name = u"活动"
        verbose_name_plural = u"活动"

    def __unicode__(self):
        return u"活动"
