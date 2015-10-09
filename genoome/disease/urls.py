#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse_lazy

from . import views

urlpatterns = [
    url(r'^upload/$', views.UploadGenome.as_view(), name='upload_genome'),
    url(r'^upload-success/(?P<pk>[0-9]+)/$', csrf_exempt(login_required(views.UploadGenomeSuccessView.as_view(), login_url=reverse_lazy('accounts:signin'))), name='upload_success'),
    url(r'^browse/$', login_required(views.DisplayGenomeResult.as_view(), login_url=reverse_lazy('accounts:signin')), name='browse_genome'),
    url(r'^description/(?P<pk>[0-9]+)/$', views.allele_description, name='description'),
    url(r'^payment-status/$', csrf_exempt(views.PaymentStatusView.as_view()), name='payment_status'),
]