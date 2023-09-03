import os
import binascii
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail.message import EmailMultiAlternatives
from django.utils import timezone
from django.db import models

# Срок действия токен на сброс пароля
EXPIRY_PERIOD = 3    # дни


class EmailUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, name='',
                     **extra_fields):
        """
        Создает и сохраняет пользователя с указанной электронной почтой и паролем.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Пользователи должны иметь адрес электронной почты.')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now, date_joined=now,
                          name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, name='', is_staff=False, **extra_fields):
        return self._create_user(email, password, is_staff=is_staff, is_superuser=False,
                                 name=name, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, is_staff=True, is_superuser=True,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Абстрактный базовый класс, реализующий полнофункциональную
    модель пользователя с правами, совместимыми с административными функциями.

    Требуются электронная почта и пароль. Остальные поля являются необязательными.
    """
    objects = EmailUserManager()

    name = models.CharField('ФИО', max_length=30, blank=True)
    email = models.EmailField('Почта', max_length=255, unique=True)
    phone = models.CharField('Телефон', max_length=20, null=True, blank=True)
    is_staff = models.BooleanField(
        'Администратор сайта', default=False,
        help_text='Определяет, может ли пользователь войти в этот административный сайт.')
    is_active = models.BooleanField(
        'Активный', default=True,
        help_text='Определяет, следует ли рассматривать этого пользователя как активного. '
                    'Снимите это выделение вместо удаления учетных записей.')
    date_joined = models.DateTimeField('Дата регистрации', default=timezone.now)

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


def _generate_code():
    return binascii.hexlify(os.urandom(20)).decode('utf-8')


def send_multi_format_email(template_prefix, template_ctxt, target_email):
    subject_file = 'accountapp/%s_subject.txt' % template_prefix
    txt_file = 'accountapp/%s.txt' % template_prefix
    html_file = 'accountapp/%s.html' % template_prefix

    subject = render_to_string(subject_file).strip()
    from_email = settings.EMAIL_FROM
    to = target_email
    text_content = render_to_string(txt_file, template_ctxt)
    html_content = render_to_string(html_file, template_ctxt)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


class PasswordResetCodeManager(BaseUserManager):
    def create_password_reset_code(self, user):
        code = _generate_code()
        return self.create(user=user, code=code)

    def get_expiry_period(self):
        return EXPIRY_PERIOD


class PasswordResetCode(models.Model):
    objects = PasswordResetCodeManager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField('code', max_length=40, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Код сброса пароля'
        verbose_name_plural = 'Коды для сброса пароля'

    def send_email(self, prefix):
        ctxt = {
            'email': self.user.email,
            'name': self.user.name,
            'code': self.code
        }
        send_multi_format_email(prefix, ctxt, target_email=self.user.email)

    def __str__(self):
        return self.code

    def send_password_reset_email(self):
        prefix = 'password_reset_email'
        self.send_email(prefix)

