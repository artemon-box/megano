from django import forms
from django.contrib import admin
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

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        current_user = request.user

        if current_user.groups.filter(name=GROUP_MODERATOR).exists():
            fields_moderator = [field for field in self.fields if field != 'is_superuser']
            return (
                (None, {'fields': fields_moderator}),
            )
        return fieldsets

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()]) if obj.groups.exists() else ""

    get_groups.short_description = 'ГРУППА'


@admin.register(PasswordResetCode)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', )
    search_fields = ['user', ]


class GroupAdminForm(forms.ModelForm):
    """
    ModelForm, который добавляет дополнительное поле множественного выбора
    для управления пользователями в группе.
    """
    users = forms.ModelMultipleChoiceField(
        get_user_model().objects.filter(is_superuser=False).all(),
        widget=admin.widgets.FilteredSelectMultiple('Пользователи', False),
        required=False,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            initial_users = self.instance.user_set.values_list('pk', flat=True)
            self.initial['users'] = initial_users
            if not kwargs['user'].is_superuser:
                self.fields['permissions'].widget = forms.HiddenInput()

    def save(self, *args, **kwargs):
        kwargs['commit'] = True
        return super(GroupAdminForm, self).save(*args, **kwargs)

    def save_m2m(self):
        self.instance.user_set.clear()
        self.instance.user_set.add(*self.cleaned_data['users'])


class NewGroupAdmin(origGroupAdmin):
    """
    Настраиваемый класс GroupAdmin, использующий настраиваемую форму
    для управления пользователями внутри группы.
    """
    form = GroupAdminForm

    def get_form_kwargs(self, request, obj=None, **kwargs):
        result = super().get_form_kwargs(request, obj, **kwargs)
        result['user'] = request.user
        return result


admin.site.unregister(Group)
admin.site.register(Group, NewGroupAdmin)

