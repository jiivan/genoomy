#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.conf.urls import url

from django.contrib.auth.views import login, logout
from . import views
from .forms import SignInForm

urlpatterns = [
    url(r'^logout/$', logout, {'next_page': reverse_lazy('landing_page')}, name='logout'),
    url(r'^signin/$', login, {'template_name': 'signin.html', 'authentication_form': SignInForm}, name='signin'),
    url(r'^signup/$', views.SignUpView.as_view(), name='signup'),
    url(r'^activate/$', views.AccountActivateView.as_view(), name='activate_account'),
    url(r'^signup-success/$', views.SignupSuccessView.as_view(), name='signup_success'),
    url(r'^save-email/$', views.UserCreateWithEmail.as_view(), name='create_with_email'),
    url(r'^save-email-succes/$', views.UserCreateSuccess.as_view(), name='create_with_email_success'),
    url(r'^profile/$', views.UserProfileView.as_view(), name='profile'),
    # url(r'^view/$', views.special_case_2003),
]