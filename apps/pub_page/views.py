# -*- coding: utf-8 -*-
import json

from django.shortcuts import render, render_to_response, get_object_or_404

import models


def index(request):
    return render(request, 'pub_page/index.html')

def intro(request):
    return render(request, 'pub_page/intro.html')
def news(request):
    return render(request, 'pub_page/news.html')
def articles(request):
    return render(request, 'pub_page/articles.html')


def article_detail(request, article_id):
    article = get_object_or_404(models.Article, id=article_id)

    if not article:
        raise
    data = {
        "article": vars(article)
    }


    return render_to_response("pub_page/article_detail.html", data)

def feelings(request):
    return render(request, 'pub_page/feelings.html')
def train_classes(request):
    return render(request, 'pub_page/train_classes.html')


#
#def content_lists(request):
#    return
#
#def content(request):
#    return
#
#def volunteer(request):
#    return

