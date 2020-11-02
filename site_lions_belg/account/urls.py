from django.conf.urls import url

from . import views

# app_name - пространство имен. Необходимо для обращения через тег url
app_name = "account"

urlpatterns = [
    url(r'^about_sportsman/(?P<sportsman_name>[-\w]+)/$', views.account_index, name='account_index'),
    url(r'^edit/(?P<sportsman_name>[-\w]+)/$', views.account_edit, name='account_edit'),
    url(r'^tournaments/', views.account_tournaments, name='account_tournaments'),
    url(r'^rating/', views.account_rating, name='account_rating'),
    url(r'^selection/', views.account_selection, name='account_selection'),
    # url(r'^tournaments/(?P<tournam_id>\d+)', views.account_tournaments, name='account_tournaments'),
    # url(r'^error_massage/$', views.account_error_massage, name='account_error_massage'),
    # url(r'^category/(?P<category_slug>[-\w]+)/$', views.category_detail, name='category_detail'),
    # url(r'^category/(?P<category_slug>[-\w]+)/(?P<page_number>\d+)/$', views.category_detail, name='category_detail'),
    # url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.tag_detail, name='tag_detail'),
    # url(r'^tag/(?P<tag_slug>[-\w]+)/(?P<page_number>\d+)/$', views.tag_detail, name='tag_detail'),
    # url(r'^(?P<new_slug>[-\w]+)/$', views.new_detail, name='new_detail')
]