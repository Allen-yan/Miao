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
    (0, "DELETED"),
    (1, "NORMAL"),
)


class BaseModel(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True, blank=True)
    # 0-deleted, 1-normal, ...
    status = models.IntegerField(default="1", choices=STATUS)


class Volunteers(BaseModel):
    #id = models.AutoField(primary_key=True)
    account = models.CharField(u"用户名", max_length=50, unique=True)
    password = models.CharField(u"用户名", max_length=50)
    name = models.CharField(u"真实名称", max_length=50, null=True, blank=True)
    nick_name = models.CharField(u"昵称", max_length=50, null=True, blank=True)
    en_name = models.CharField(u"英文名称", max_length=50, null=True, blank=True)
    sex = models.CharField(u"性别", max_length=1, choices=SEX_CHOICE)
    age = models.IntegerField(u"年龄", null=True, blank=True)
    phone_number = models.CharField(u"联系方式", max_length=50)

    level = models.IntegerField(u"级别",  choices=USER_LEVEL)


class CheckIn(BaseModel):
    volunteer_id = models.ForeignKey(Volunteers)


class Classes(BaseModel):
    #id = models.AutoField(primary_key=True)
    class_name = models.CharField(u"班级", max_length=50, null=True, blank=True)
    grade = models.CharField(u"年级", max_length=50, null=True, blank=True)
    contact = models.CharField(u"联系人", max_length=50, null=True, blank=True)
    school_name = models.CharField(u"学校名称", max_length=50, null=True, blank=True)
    student_count = models.IntegerField(u"学生人数")


class Courses(BaseModel):
    #id = models.AutoField(primary_key=True)
    course_name = models.CharField(u"课程名称", max_length=50, null=True, blank=True)


class ClassBegin(BaseModel):
    #id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Courses)
    class_id = models.ForeignKey(Classes)
    volunteer_id = models.ForeignKey(Volunteers)
    course_name = models.CharField(u"课程名称", max_length=50, null=True, blank=True)

    # multi primary keys
    class Meta:
        unique_together = ("course_id", "class_id", "volunteer_id")