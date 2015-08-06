#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import models as auth_models
from django.contrib.auth.forms import UserCreationForm

class EmailUserCreateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = auth_models.User
        fields = ['email']

    def save(self, commit=True):
        self.instance.username = self.cleaned_data.get('email', '')
        return super().save(commit)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = ('email',)

    def save(self, commit=True):
        self.instance.username = self.cleaned_data.get('email', '')
        return super().save(commit)
