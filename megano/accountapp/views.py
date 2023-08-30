from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views import View
from .accounts import cmd_create_buyer
from .forms import RegistrationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required


class RegistrationView(View):
    TEMPLATE_NAME = 'registration.jinja2'
    form_class = RegistrationForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.TEMPLATE_NAME, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['login']
            password = form.cleaned_data['password']
            user = cmd_create_buyer(name=name, email=email, password=password)
            if user is not None:
                # Успешная регистрация
                user = authenticate(username=email, password=password)
                if user is not None:
                    login(request, user)
                return redirect('/')
        else:
            # Форма не прошла валидацию, возвращаем с ошибками
            return render(request, self.TEMPLATE_NAME, {'form': form})
        return render(request, self.TEMPLATE_NAME)


class LoginView(View):
    TEMPLATE_NAME = 'login.jinja2'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/')
        return render(request, self.TEMPLATE_NAME, {'error_message': ''})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('/')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Перенаправление на главную страницу после входа
        else:
            return render(request, self.TEMPLATE_NAME, {'error_message': 'Неверная почта или пароль.'})


class LogoutView(LogoutView):
    next_page = '/'


def password_reset(request):
    return render(request, 'password_reset.jinja2')


def password_reset_confirm(request):
    return render(request, 'password_reset_confirm.jinja2')

