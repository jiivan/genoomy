#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.login23, name='login'),
    url(r'^comeback/$', views.comeback, name='comeback'),
    url(r'^profiles/$', views.profiles, name='profiles'),
    url(r'^status/$', views.status, name='status'),
]
