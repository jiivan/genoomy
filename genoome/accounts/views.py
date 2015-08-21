import os

from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.template.loader import get_template
from django.shortcuts import render_to_response

from accounts.forms import ActivateAccountForm
from accounts.forms import EmailUserCreateForm
from accounts.forms import SignUpForm

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
    success_url = reverse_lazy('accounts:signup_success')
    template_name = 'signup.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            user = self.model.objects.get(email=kwargs.get('data', {}).get('email', [None]))
            kwargs.update({'instance': user})
        except self.model.DoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        ctx = {}
        if self.object.is_active:
            ctx['activated'] = True
            messages.success(self.request, 'Your account is now active.You can now log in.')
        resp = render_to_response('signup_success.html', context=ctx)
        return resp

    def get_template_names(self):
        if self.request.is_ajax():
            return 'signup_modal.html'
        return 'signup.html'


class SignupSuccessView(TemplateView):
    template_name = 'signup_success.html'

class UserProfileView(TemplateView):
    template_name = 'user_profile.html'

    def get_genome_dirpath(self):
        app_dir = 'disease'
        user_subdir = '{}:{}'.format(self.request.user.pk, self.request.user.email)
        return storage.path(os.path.join(app_dir, user_subdir))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        dirpath = self.get_genome_dirpath()
        if os.path.exists(dirpath):
            _, files = storage.listdir(dirpath)
            processed_files = []
            for file in files:
                filename, ext = file.rsplit('.', 1)
                if filename.endswith('_processed'):
                    original_filename, _ = filename.rsplit('_', 1)
                    processed_files.append(''.join([original_filename, '.', ext]))
            ctx['saved_genome_data'] = processed_files
        return ctx

class AccountActivateView(SuccessMessageMixin, FormView):
    template_name = 'activate_account.html'
    form_class = ActivateAccountForm
    success_url = reverse_lazy('accounts:profile')
    success_message = 'Your account is now active.You can no log in.'

    def form_valid(self, form):
        form.activate_user()
        return super().form_valid(form)
