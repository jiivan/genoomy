#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.conf.urls import url
from django.contrib.auth.views import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views
from .forms import SignInForm

urlpatterns = [
    url(r'^logout/$', logout, {'next_page': reverse_lazy('landing_page')}, name='logout'),
    url(r'^signin/$', login, {'template_name': 'signin.html', 'authentication_form': SignInForm}, name='signin'),
    url(r'^signup/$', views.SignUpView.as_view(), name='signup'),
    url(r'^activate/$', views.AccountActivateView.as_view(), name='activate_account'),
    url(r'^contact/$', views.ContactFormView.as_view(), name='contact'),
    url(r'^signup-success/$', views.SignupSuccessView.as_view(), name='signup_success'),
    url(r'^save-email/$', views.UserCreateWithEmail.as_view(), name='create_with_email'),
    url(r'^save-email-succes/$', views.UserCreateSuccess.as_view(), name='create_with_email_success'),
    url(r'^profile/$', csrf_exempt(login_required(views.UserProfileView.as_view(), login_url='/accounts/signin')), name='profile'),
    url(r'^disable/$', login_required(views.AccountDisableView.as_view()), name='disable')
    # url(r'^view/$', views.special_case_2003),
]