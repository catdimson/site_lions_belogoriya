from django.conf.urls import url

from . import views

# app_name - пространство имен. Необходимо для обращения через тег url
app_name = "news"

urlpatterns = [
    url(r'^$', views.base_news_list, name='news_list'),
    url(r'^(?P<page_number>\d+)/$', views.base_news_list, name='news_list'),
    url(r'^category/(?P<category_slug>[-\w]+)/$', views.category_detail, name='category_detail'),
    url(r'^category/(?P<category_slug>[-\w]+)/(?P<page_number>\d+)/$', views.category_detail, name='category_detail'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.tag_detail, name='tag_detail'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/(?P<page_number>\d+)/$', views.tag_detail, name='tag_detail'),
    url(r'^(?P<new_slug>[-\w]+)/$', views.new_detail, name='new_detail')
]
