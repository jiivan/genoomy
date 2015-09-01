from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client

from accounts.forms import SignUpForm

client = Client()


class UserSignupFormTests(TestCase):
    def test_presence_of_fields(self):
        fields_included = ('email',)
        fields_excluded = ('username', 'code',)  # Regression test
        fields = SignUpForm().fields
        self.assertTrue(all(k in fields for k in fields_included))
        self.assertTrue(all(k not in fields for k in fields_excluded))

    def test_email_field_required(self):
        data = dict(password1='test', password2='test')

        form = SignUpForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('email', 'required'))
        self.assertFalse(form.has_error('email', 'anything'))

    def test_user_creation(self):
        data = dict(username='testuser', email='test@example.uu', password1='tests',
                    password2='tests')
        form = SignUpForm(data)
        self.assertTrue(form.is_valid())
        form.save()
        user = get_user_model().objects.get(email='test@example.uu')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class UserSignUpTests(TestCase):
    def test_signed_up_user_is_active(self):
        post_params = dict(username='testuser', email='test@example.uu', password1='tests',
                           password2='tests')
        client.post(reverse('accounts:signup'), post_params)

        # Username of regular users are their emails
        user = get_user_model().objects.get(username='test@example.uu')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
