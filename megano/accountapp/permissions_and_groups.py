from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
CODENAME='codename'
NAME='name'
GROUP_SUPERUSER = 'superuser'
GROUP_MODERATOR = 'moderator'
GROUP_BUYER = 'buyer'

VIEW_PAGE_PERMISSIONS = {CODENAME: 'can_view_page', NAME: 'Просмотр страниц'}
EDIT_CARD_PRODUCT_PERMISSIONS = {CODENAME: 'can_edit_card_product', NAME: 'Создание и изменение карточек товара'}

group_names = {
    GROUP_SUPERUSER: [
        VIEW_PAGE_PERMISSIONS,
        EDIT_CARD_PRODUCT_PERMISSIONS,
    ],
    GROUP_MODERATOR: [
        VIEW_PAGE_PERMISSIONS,
    ],
    GROUP_BUYER: [
        VIEW_PAGE_PERMISSIONS,
    ],
}


def create_groups_and_permissions(apps, schema_editor):
    # Создание группы
    for group_name in group_names:
        group, created = Group.objects.get_or_create(name=group_name)

    # Создание или чтение разрешения и присвоение к группе
        for permission_item in group_names[group_name]:
            permission_item[CODENAME] = permission_item[CODENAME].lower()
            content_type, created2 = ContentType.objects.get_or_create(
                app_label='accountapp',  # Replace with your app's label
                model='accountapp_user'  # Replace with your model's name
            )
            permission, created = Permission.objects.get_or_create(codename=permission_item[CODENAME],
                                                                   name=permission_item[NAME],
                                                                    content_type=content_type)
            group.permissions.add(permission)


def set_group_user(user, group_name):
    """
    Установить пользователю группу
    """
    group = Group.objects.get(name=group_name)
    group.user_set.add(user)