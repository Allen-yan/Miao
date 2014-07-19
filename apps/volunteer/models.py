# -*- encoding:utf-8 -*-
from django.db import models

SEX_CHOICE = (
    ("M", "male"),
    ("F", "female")
)

USER_LEVEL = (
    (0, "admin"),
    (1, "ordinary user")
)


STATUS = (
    (0, u"禁用"),
    (1, u"正常"),
)


class BaseModel(models.Model):
    created_at = models.DateTimeField(u"时间", null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    # 0-deleted, 1-normal, ...
    status = models.IntegerField(default="1", choices=STATUS)

    # Abstract class . Will not generate a table
    class Meta:
        abstract = True


class Volunteer(BaseModel):
    #id = models.AutoField(primary_key=True)
    account = models.CharField(u"用户名", max_length=50, unique=True)
    password = models.CharField(u"密码", max_length=50)
    name = models.CharField(u"真实名称", max_length=50, null=True, blank=True)
    nick_name = models.CharField(u"昵称", max_length=50, null=True, blank=True)
    en_name = models.CharField(u"英文名称", max_length=50, null=True, blank=True)
    sex = models.CharField(u"性别", max_length=1, choices=SEX_CHOICE)
    age = models.IntegerField(u"年龄", null=True, blank=True)
    phone_number = models.CharField(u"联系方式", max_length=50)

    level = models.IntegerField(u"级别",  choices=USER_LEVEL)

    class Meta:
        verbose_name = u"志愿者"
        verbose_name_plural = u"志愿者"

    def __unicode__(self):
        return self.account


class Group(BaseModel):
    group_name = models.CharField(u"小组名称", max_length=50, unique=True)

    class Meta:
        verbose_name = u"志愿者小组"
        verbose_name_plural = u"志愿者小组"

    def __unicode__(self):
        return self.account


class CheckIn(BaseModel):
    volunteer_id = models.ForeignKey(Volunteer, related_name="volunteer")

    class Meta:
        verbose_name = u"签到"
        verbose_name_plural = u"签到"

    def __unicode__(self):
        return unicode(self.volunteer_id)

class Class(BaseModel):
    #id = models.AutoField(primary_key=True)
    class_name = models.CharField(u"班级", max_length=50)
    grade = models.CharField(u"年级", max_length=50)
    contact = models.CharField(u"联系人", max_length=50, null=True, blank=True)
    school_name = models.CharField(u"学校名称", max_length=50, null=True, blank=True)
    student_count = models.IntegerField(u"学生人数")

    class Meta:
        verbose_name = u"班级"
        verbose_name_plural = u"班级"

    def __unicode__(self):
        return self.class_name


class School(BaseModel):
    #id = models.AutoField(primary_key=True)
    school_name = models.CharField(u"学校名称", max_length=50)
    description = models.CharField(u"描述", max_length=50, null=True, blank=True)
    contact = models.CharField(u"联系人", max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = u"学校"
        verbose_name_plural = u"学校"

    def __unicode__(self):
        return self.class_name


class Course(BaseModel):
    #id = models.AutoField(primary_key=True)
    course_name = models.CharField(u"课程名称", max_length=50)

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = u"课程"

    def __unicode__(self):
        return self.course_name


class ClassBegin(BaseModel):
    #id = models.AutoField(primary_key=True)

    course_id = models.ForeignKey(Course, related_name="aaa")
    class_id = models.ForeignKey(Class, related_name="bbb")
    volunteer_id = models.ForeignKey(Volunteer, related_name="ccc")
    #course_name = models.CharField(u"课程名称", max_length=50, null=True, blank=True)

    class Meta:
        # multi primary keys
        unique_together = ("course_id", "class_id", "volunteer_id")
        verbose_name = u"上课情况"
        verbose_name_plural = u"上课情况"

    def __unicode__(self):
        return u"上课信息"