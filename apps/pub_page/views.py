# -*- coding: utf-8 -*-

from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import render, render_to_response, get_object_or_404, HttpResponseRedirect

import models
import settings

def json_default_processor(obj):
    if isinstance(obj, models.Article):
        return vars(obj)

def index(request):
    show_count = 5
    data = {
        "reading_classes": models.Article.objects.filter(article_type='1')[:show_count],
        "train_classes": models.Article.objects.filter(article_type='2')[:show_count],
        "reading_show": models.Article.objects.filter(article_type='3')[:show_count],
        "feelings": models.Article.objects.filter(article_type='4')[:show_count],
    }
    return render_to_response('pub_page/index.html', data)

def intro(request):
    return render(request, 'pub_page/intro.html')


def news(request):
    # news: article type 5
    news_page_list = get_articles_page_list('5', request.GET.get("page", 1))

    return render_to_response(
        'pub_page/news.html',
        {"data": news_page_list}
    )


def news_detail(request, news_id):
    article = get_object_or_404(models.Article, id=news_id)

    if not article:
        raise
    data = {
        "article": vars(article)
    }

    return render_to_response("pub_page/article_detail.html", data)


def get_articles_page_list(article_type, selected_page=1):
    art_list = models.Article.objects.filter(article_type=article_type)
    paginator = Paginator(art_list, settings.ARTICLE_LIST_COUNT)

    try:
        page_art = paginator.page(selected_page)
    except (EmptyPage, InvalidPage):
        page_art = paginator.page(1)

    return page_art


def feelings(request):
    return render(request, 'pub_page/feelings.html')


def train_classes(request):
    return render(request, 'pub_page/train_classes.html')
