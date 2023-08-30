from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.db import models


class EmailUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser,
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
                          is_superuser=is_superuser, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, is_staff=False, is_superuser=False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, is_staff=True, is_superuser=True,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Абстрактный базовый класс, реализующий полнофункциональную
    модель пользователя с правами, совместимыми с административными функциями.

    Требуются электронная почта и пароль. Остальные поля являются необязательными.
    """
    last_name = models.CharField('Фамилия', max_length=30, blank=True)
    first_name = models.CharField('Имя', max_length=30, blank=True)
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
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    objects = EmailUserManager()
