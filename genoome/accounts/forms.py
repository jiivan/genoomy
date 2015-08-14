#!/usr/bin/env python
# -*- coding: utf-8 -*-
from coupons.forms import CouponForm
from coupons.models import Coupon
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import models as auth_models
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

user_model = get_user_model()

class SignInForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _("Please enter a correct %(username)s and password. "
                           "Note that both fields may be case-sensitive."),
        'inactive': _("This account is inactive. You need activation code to login."),
    }


class EmailUserCreateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = user_model
        fields = ['email']

    def save(self, commit=True):
        self.instance.username = self.cleaned_data.get('email', '')
        return super().save(commit)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    code = forms.CharField(label=_("Coupon code"))

    class Meta(UserCreationForm.Meta):
        model = user_model
        fields = ('email',)

    def clean_code(self):
        code = self.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise forms.ValidationError(_("This code is not valid."))
        if coupon.expired():
            raise forms.ValidationError(_("This code is expired."))
        return code

    def save(self, commit=True):
        self.instance.username = self.cleaned_data.get('email', '')
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class ActivateAccountForm(CouponForm):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if not user_model.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Account does not exist",
                code='no_account')
        return email

    def activate_user(self):
        email = self.cleaned_data['email']
        user = user_model.objects.get(email=email)
        user.is_active = True
        user.save()
