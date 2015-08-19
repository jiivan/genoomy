#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^upload/$', login_required(views.UploadGenome.as_view(), login_url='/accounts/signup/'), name='upload_genome'),
    url(r'^browse/$', login_required(views.DisplayGenomeResult.as_view(), login_url='/accounts/signin/'), name='browse_genome'),
    # url(r'^view/$', views.special_case_2003),
]