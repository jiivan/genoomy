#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^save-email/$', views.UserCreateWithEmail.as_view(), name='create_with_email'),
    url(r'^save-email-succes/$', views.UserCreateSuccess.as_view(), name='create_with_email_success'),
    # url(r'^view/$', views.special_case_2003),
]