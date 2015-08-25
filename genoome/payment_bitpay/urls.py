#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^initiate-payment/(?<payment_id>)/$', login_required(views.InitiatePaymentView.as_view(), login_url=reverse_lazy('accounts:signup')), name='initiate_payment'),
]