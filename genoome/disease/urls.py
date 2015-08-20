#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy

from . import views

urlpatterns = [
    url(r'^upload/$', login_required(views.UploadGenome.as_view(), login_url=reverse_lazy('accounts:signin')), name='upload_genome'),
    url(r'^browse/$', login_required(views.DisplayGenomeResult.as_view(), login_url=reverse_lazy('accounts:signin')), name='browse_genome'),
    # url(r'^view/$', views.special_case_2003),
]