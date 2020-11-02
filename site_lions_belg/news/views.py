from django.shortcuts import render
from django.http import HttpResponse
from .models import CategoryNews, New, TagNews
from django.core.paginator import Paginator

# Create your views here.


def base_news_list(request, page_number=1):
    categories = CategoryNews.objects.all()
    news = New.objects.all()
    categories, tags = get_tags_and_categories(categories, news)
    news = Paginator(news, 6).page(page_number)
    context = {
        'categories': categories,
        'news': news,
        'tags': tags,
        'lvl': 'news'
    }
    return render(request, 'news/index_news.html', context)


def category_detail(request, category_slug, page_number=1):
    category = CategoryNews.objects.get(slug=category_slug)
    categories = CategoryNews.objects.all()
    news = New.objects.filter(category=category)
    categories, tags = get_tags_and_categories(categories, New.objects.all())
    news = Paginator(news, 6).page(page_number)
    context = {
        'categories': categories,
        'category': category,
        'news': news,
        'tags': tags,
        'lvl': 'category',
        'slug': category_slug
    }
    return render(request, 'news/index_news.html', context)


def tag_detail(request, tag_slug, page_number=1):
    tag = TagNews.objects.get(slug=tag_slug)
    categories = CategoryNews.objects.all()
    news = New.objects.filter(tag=tag)
    categories, tags = get_tags_and_categories(categories, New.objects.all())
    news = Paginator(news, 6).page(page_number)
    context = {
        'categories': categories,
        'tag': tag,
        'news': news,
        'tags': tags,
        'lvl': 'tag',
        'slug': tag_slug
    }
    return render(request, 'news/index_news.html', context)


def new_detail(request, new_slug):
    new = New.objects.get(slug=new_slug)
    categories = CategoryNews.objects.all()
    categories, tags = get_tags_and_categories(categories, New.objects.all())
    context = {
        'categories': categories,
        'tags': tags,
        'new': new
    }
    return render(request, 'news/new_detail.html', context)


# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# кастомная функция для фильтрации категорий и тегов, к которым не относится ни одна новость
def get_tags_and_categories(categories, news):
    storage_results = []
    for cat in categories:
        if not (len(cat.new_set.all()) == 0):
            storage_results.append(cat)
    categories = storage_results[:]

    storage_results = set()
    for new in news:
        for t in new.tag.all():
            storage_results.add(t)
    print(" #POINT 460 - cats: {0}".format(categories))
    print(" #POINT 460.1 - tags: {0}".format(storage_results))
    return categories, storage_results


