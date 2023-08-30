from .permissions_and_groups import set_group_user, GROUP_SELLER, GROUP_MODERATOR
from django.contrib.auth import get_user_model


def cmd_create_superuser(email,password):
    """
    Команда создать суперюзера
    """
    return get_user_model().objects.create_superuser(email, password)


def cmd_create_moderator(email,password):
    """
    Команда создать модератора
    """
    user = get_user_model().objects.create_user(email, password)
    set_group_user(user, GROUP_MODERATOR)
    return user


def cmd_create_seller(email,password):
    """
    Команда создать продавца
    """
    user = get_user_model().objects.create_user(email, password)
    set_group_user(user, GROUP_SELLER)
    return user
