#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import models as auth_models

class EmailUserCreateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = auth_models.User
        fields = ['email']

    def save(self, commit=True):
        self.instance.username = self.cleaned_data.get('email', '')
        return super().save(commit)



