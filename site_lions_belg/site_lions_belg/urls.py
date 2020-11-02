# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

admin.autodiscover()

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {'cmspages': CMSSitemap}}),
    url(r'^registration/', include('registration.urls')),
    url(r'^account/', include('account.urls')),
    # url(r'^polls/', include('polls.urls')),
    # url(r'^', include('djangocms_forms.urls')),

    # Задания из учебника (приложение uchebnik. Его необходимо удалить. Вычистить базу, связанную с ним)
    # url(r'^goods/', include('uchebnik.urls')),
    # Уроки Олега Молчанова по Django 2
    # url(r'^blog/', include('blog_molchanov.urls')),
    url(r'^admin/', admin.site.urls),  # NOQA
    url(r'^', include('cms.urls')),
]

# urlpatterns += i18n_patterns(
#
# )

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns
