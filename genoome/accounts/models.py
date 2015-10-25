from django.contrib.auth import models as auth_models
from django.core import validators
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from disease.files_utils import get_genome_dirpath

import time

storage = FileSystemStorage()


class GenoomyAbstractUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    """
    Shameless copy of django auth model which sole purpose is to increase max_length of some fields
    """
    username = models.CharField(_('username'), max_length=80, unique=True,
        help_text=_('Required. 80 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })
    first_name = models.CharField(_('first name'), max_length=80, blank=True)
    last_name = models.CharField(_('last name'), max_length=80, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = auth_models.UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def disable(self):
        """
        Disables user account.
        """
        self.is_active = False
        self.email = self.username = \
            '%s-disabled.%d' % (self.username, time.time())


class GenoomyUser(GenoomyAbstractUser):
    FILES_PER_USER = 1

    class Meta(GenoomyAbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    @property
    def uploaded_files(self):
        files = []
        dirpath = get_genome_dirpath(self)
        if storage.exists(dirpath):
            _, files = storage.listdir(storage.path(dirpath))
        for file in files:
            filename, ext = file.rsplit('.', 1)
            if not filename.endswith('_processed'):
                yield file

    @property
    def can_upload_files(self):
        files = list(self.uploaded_files)
        can_upload = bool(len(files) < self.FILES_PER_USER)
        return bool(can_upload or (self.is_staff and self.is_active))