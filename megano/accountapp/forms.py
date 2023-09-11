from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model


class RegistrationForm(forms.Form):
    name_regex = RegexValidator(
        regex=r'^[а-яА-ЯёЁa-zA-Z]+\s[а-яА-ЯёЁa-zA-Z]+\s[а-яА-ЯёЁa-zA-Z]+$',
        message="Введите Фамилию, Имя и Отчество полностью",
    )

    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'user-input'}), validators=[name_regex])
    login = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'user-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'user-input'}))

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 8:  # Пример минимальной длины имени
            self.add_error('name', "Поле должно содержать не менее 8 символов.")
        return name

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:  # Пример минимальной длины пароля
            self.add_error('password', "Пароль должен содержать не менее 8 символов.")
        return password

    def clean_login(self):
        email = self.cleaned_data['login']
        if get_user_model().objects.filter(email=email).exists():
            self.add_error('login', "Этот адрес электронной почты уже зарегистрирован.")
        return email


class PasswordResetForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'user-input'}))


class PasswordNewForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'user-input'}))
