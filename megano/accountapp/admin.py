from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin
from .models import PasswordResetCode
from django.contrib.auth.admin import GroupAdmin as origGroupAdmin
from django.contrib.auth.models import Group
from django.contrib.admin.widgets import FilteredSelectMultiple
from .permissions_and_groups import GROUP_MODERATOR
from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class MyUserAdmin(admin.ModelAdmin):
    fields = ['email', 'name', 'phone', 'last_login', 'is_staff', 'is_superuser', 'is_active', 'date_joined', ]
    list_display = ('email', 'name', 'is_staff', 'get_groups')
    search_fields = ['name', 'email', ]
    ordering = ('-is_staff', 'email', )

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()]) if obj.groups.exists() else ""

    get_groups.short_description = 'ГРУППА'

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name=GROUP_MODERATOR).exists():
            return True
        return super().has_change_permission(request, obj)


@admin.register(PasswordResetCode)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', )
    search_fields = ['user', ]


class GroupAdminForm(forms.ModelForm):
    """
    ModelForm that adds an additional multiple select field for managing
    the users in the group.
    """
    users = forms.ModelMultipleChoiceField(
        get_user_model().objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Users', False),
        required=False,
        )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            initial_users = self.instance.user_set.values_list('pk', flat=True)
            self.initial['users'] = initial_users

    def save(self, *args, **kwargs):
        kwargs['commit'] = True
        return super(GroupAdminForm, self).save(*args, **kwargs)

    def save_m2m(self):
        self.instance.user_set.clear()
        self.instance.user_set.add(*self.cleaned_data['users'])


class GroupAdmin(origGroupAdmin):
    """
    Customized GroupAdmin class that uses the customized form to allow
    management of users within a group.
    """
    form = GroupAdminForm
    def has_view_permission(self, request, obj=None):
        print('hh')
        if request.user.groups.filter(name=GROUP_MODERATOR).exists():
            return True
        return super().has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name=GROUP_MODERATOR).exists():
            return True
        return super().has_change_permission(request, obj)


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

