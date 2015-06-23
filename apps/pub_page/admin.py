from django.contrib import admin

import models

class ArticleAdmin(admin.ModelAdmin):

    list_display = ["title", "publish_time", "summary"]

admin.site.register(models.Article, ArticleAdmin)
