from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.views.generic import TemplateView
from django.template.loader import get_template
from django.shortcuts import render_to_response

from accounts.forms import EmailUserCreateForm
from accounts.forms import SignUpForm

# Create your views here.
class UserCreateWithEmail(CreateView):
    template_name = 'save_email.html'
    form_class = EmailUserCreateForm
    model = User
    # fields = ('email',)
    success_url = reverse_lazy('accounts:create_with_email_success')

    def form_valid(self, form):
        resp = super().form_valid(form)
        template = get_template('save_email_success.html')
        resp.template = template
        return resp

class UserCreateSuccess(TemplateView):
    template_name = 'save_email_success.html'


class SignUpView(CreateView):
    form_class = SignUpForm
    model = User
    success_url = reverse_lazy('accounts:signup_success')
    template_name = 'signup.html'

    def form_valid(self, form):
        resp = super().form_valid(form)
        template = get_template('signup_success.html')
        resp.template = template
        return resp


class SignupSuccessView(TemplateView):
    template_name = 'signup_success.html'
