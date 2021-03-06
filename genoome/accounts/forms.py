#!/usr/bin/env python
# -*- coding: utf-8 -*-
from coupons.forms import CouponForm
from coupons.models import Coupon
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import EMPTY_VALUES
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm as AuthPasswordResetForm
from django.utils.translation import ugettext_lazy as _

user_model = get_user_model()


class SignInForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _("Please enter a correct email and password. "
                           "Note that both fields may be case-sensitive."),
        'inactive': _("This account is inactive. You need activation code to login."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'


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

    class Meta(UserCreationForm.Meta):
        model = user_model
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        if user_model.objects.filter(username=email).count():
            raise ValidationError('User with this email already exists')

        return email

    def save(self, commit=True):
        self.instance.username = self.cleaned_data.get('email', '')
        user = super().save(commit=commit)
        return user


class ActivateAccountForm(forms.Form):
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


class ContactForm(forms.Form):
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        user_email = self.cleaned_data['email']
        message = self.cleaned_data['message']
        subject = 'Contact form from {}'.format(user_email)
        send_mail(subject, message, user_email, [settings.EMAIL_HOST_USER], fail_silently=True)

class PasswordResetForm(AuthPasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not get_user_model().objects.filter(is_active=True, email__iexact=email).exists():
            raise forms.ValidationError('User with given email does not exist.', 'invalid')
        return email