import os

from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model, login, logout
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.forms import Form

from accounts.forms import ActivateAccountForm
from accounts.forms import EmailUserCreateForm
from accounts.forms import SignUpForm
from configurable_elements.models import get_legend_rows
from disease.models import CustomizedTag
from disease.files_utils import get_genome_data

storage = FileSystemStorage()
user_model = get_user_model()

class UserCreateWithEmail(CreateView):
    template_name = 'save_email.html'
    form_class = EmailUserCreateForm
    model = user_model
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
    model = get_user_model()
    success_url = reverse_lazy('accounts:profile')
    template_name = 'signup.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        self.object = form.save()  # User

        # Dirty way to login user
        self.object.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, self.object)

        ctx = {}
        if self.object.is_active:
            ctx['activated'] = True
            messages.success(self.request, 'Your account is now active. You are logged in.')
        return super().form_valid(form)

    def get_template_names(self):
        if self.request.is_ajax():
            return 'signup_modal.html'
        return 'signup.html'


class SignupSuccessView(TemplateView):
    template_name = 'signup_success.html'


class UserProfileView(TemplateView):
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['saved_genome_data'] = self.request.user.uploaded_files
        return ctx

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

class AccountActivateView(SuccessMessageMixin, FormView):
    template_name = 'activate_account.html'
    form_class = ActivateAccountForm
    success_url = reverse_lazy('accounts:profile')
    success_message = 'Your account is now active.You can no log in.'

    def form_valid(self, form):
        form.activate_user()
        return super().form_valid(form)

class AccountDisableView(SuccessMessageMixin, FormView):
    template_name = 'disable_account.html'
    form_class = Form
    success_url = reverse_lazy('landing_page')
    success_message = 'Your account is now disabled.'

    def form_valid(self, form):
        self.request.user.disable()
        self.request.user.save()
        logout(self.request)

        return super().form_valid(form)

class LandingView(TemplateView):
    template_name = 'landing.html'
    sample_data_filename = 'samplegenotype'

    def get_context_data(self, **kwargs):
        sample_data_filepath = 'disease/{}'.format(self.sample_data_filename)
        kwargs['table'] = get_genome_data(sample_data_filepath)
        kwargs['allele_tags'] = CustomizedTag.objects.filter(show_on_landing=True)
        kwargs['legend_rows'] = get_legend_rows()
        return super().get_context_data(**kwargs)
