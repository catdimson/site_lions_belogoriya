from django.conf.urls import url

from . import views

# app_name - пространство имен. Необходимо для обращения через тег url
app_name = "registration"

urlpatterns = [
    url(r'^login/', views.login, name='reg_login'),
    url(r'^logout/', views.logout, name='reg_logout'),
    url(r'^register/', views.register, name='reg_registration'),
]