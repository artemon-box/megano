from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator


class ProfileAvatarForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['avatar']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:  # размер файла в байтах для 2 МБ
                self.add_error('avatar', "Размер файла слишком большой. Размер файла не должен превышать 2 МБ.")
        return avatar

class ProfileForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^375\d{9}$',
        message="Введите номер телефона в формате: '375xxxxxxxxx'",
    )
    name_regex = RegexValidator(
        regex=r'^[а-яА-ЯёЁa-zA-Z]+\s[а-яА-ЯёЁa-zA-Z]+\s[а-яА-ЯёЁa-zA-Z]+$',
        message="Введите Фамилию, Имя и Отчество полностью",
    )

    phone = forms.CharField(validators=[phone_regex])
    name = forms.CharField(validators=[name_regex])
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    passwordReply = forms.CharField(label='Confirm password', widget=forms.PasswordInput(), required=False)

    class Meta:
        model = get_user_model()
        fields = ['name', 'phone', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если у instance есть номер телефона, добавляем "375"
        if self.instance.phone:
            self.initial['phone'] = "375" + str(self.instance.phone)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 8:  # Пример минимальной длины имени
            self.add_error('name', "Поле должно содержать не менее 8 символов.")
        return name

    def clean_email(self):
        email = self.cleaned_data['email']
        if email == self.instance.email:
            return email
        if get_user_model().objects.filter(email=email).exists():
            self.add_error('email', "Этот адрес электронной почты уже зарегистрирован.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone[3:] == self.instance.phone:
            return phone
        if get_user_model().objects.filter(phone=phone[3:]).exists():
            self.add_error('phone', "Этот номер телефона занят.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('passwordReply')

        if password and password2 and password != password2:
            self.add_error('password', "Пароли не совпадают.")
        elif password and len(password) < 8:
            self.add_error('password', "Пароль должен содержать не менее 8 символов.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.phone = instance.phone[3:]
        if commit:
            instance.save()
        return instance