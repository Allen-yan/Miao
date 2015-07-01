# -*- encoding:utf-8 -*-
from django.db import models
from django.template.defaultfilters import title
from datetime import date
from django.test.client import CONTENT_TYPE_RE

ARTICLE_CHOICE = (
    ('1', "导读课"),
    ('2', "读书经验谈"),
    ('3', "志愿者心声"),
    ('4', "志愿者培训"),
    ('5', "新闻"),
)

class Article(models.Model):
    title = models.CharField(u"标题", max_length=50, null=True, blank=True)
    article_type = models.CharField(u"文章类型", max_length=50, choices=ARTICLE_CHOICE)
    publish_time = models.TimeField(u'发布时间', null=True, blank=True, auto_created=True)
    author = models.CharField(u"作者", max_length=20, null=True, blank=True)
    content = models.TextField(u"内容")
    summary = models.CharField(u"摘要", max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = u"文章"
        verbose_name_plural = u"文章"
        permissions = (
            ("view_only_topic_detail",  u"可以查看%s相关信息" % verbose_name),
        )
    def __unicode__(self):
        return self.title