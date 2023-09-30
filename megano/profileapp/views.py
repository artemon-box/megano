import os
from django.conf import settings
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views import View
from .forms import ProfileAvatarForm, ProfileForm
from django.contrib.auth import authenticate, login


class AccountView(View):
    template_name = 'account.jinja2'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        user = request.user
        return render(request, self.template_name, {'user': user})


class ProfileView(View):
    template_name = 'profile.jinja2'
    form_class = ProfileForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form, 'user': request.user, 'saved': False})

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
                user.save()
                user = authenticate(username=email, password=password)
                if user is not None:
                    login(request, user)
        else:
            # Форма не прошла валидацию, возвращаем с ошибками
            return render(request, self.template_name, {'form': form, 'user': request.user, 'saved': False})
        return render(request, self.template_name, {'form': form, 'user': request.user, 'saved': True})


class ProfileAvatarView(APIView):
    form_class = ProfileAvatarForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = request.user

            # Удаляем старый аватар, если он есть
            if user.avatar:
                old_avatar_path = os.path.join(settings.MEDIA_ROOT, str(user.avatar))
                if os.path.isfile(old_avatar_path):
                    os.remove(old_avatar_path)

            # Генерируем новое имя файла
            email = user.email
            filename = f"{email.replace('@', '_').replace('.', '_')}_avatar{os.path.splitext(request.FILES['avatar'].name)[-1]}"

            # Сохраняем новый аватар
            user.avatar.save(filename, request.FILES['avatar'])
            user.save()
            return Response({"message": "Avatar successfully updated"}, status=200)
        error_message = 'Произошла ошибка при загрузке аватара. Пожалуйста, попробуйте еще раз.'
        if 'avatar' in form.errors:
            error_message = form.errors['avatar'][0]
        return Response({"message": error_message}, status=400)

