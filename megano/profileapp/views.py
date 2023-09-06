from django.shortcuts import render, redirect
from django.views import View
from .forms import ProfileAvatarForm


class AccountView(View):
    template_name = 'account.jinja2'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        user = request.user
        return render(request, self.template_name)


class ProfileView(View):
    template_name = 'profile.jinja2'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        user = request.user
        return render(request, self.template_name)


class ProfileAvatarView(View):
    template_name = 'profile_avatar.jinja2'
    form_class = ProfileAvatarForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        form = self.form_class()
        user = request.user
        return render(request, self.template_name, {'form': form, 'user': user})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            user.avatar = form.cleaned_data['avatar']
            user.save()
            return redirect('profile_avatar_view')
        return render(request, self.template_name, {'form': form})
