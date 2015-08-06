#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload/$', views.UploadGenome.as_view(), name='upload_genome'),
    url(r'^browse/$', views.DisplayGenomeResult.as_view(), name='browse_genome'),
    # url(r'^view/$', views.special_case_2003),
]