#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    url(r'^paypal-callback/', include('paypal.standard.ipn.urls'), name='paypal_callback'),
]
