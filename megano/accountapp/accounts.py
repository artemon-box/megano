from .permissions_and_groups import set_group_user, GROUP_SUPERUSER, GROUP_BUYER, GROUP_MODERATOR
from django.contrib.auth import get_user_model


def cmd_create_superuser(email,password):
    """
    Команда создать суперпользователя
    """
    user = get_user_model().objects.create_superuser(email, password)
    set_group_user(user, GROUP_SUPERUSER)
    return user


def cmd_create_moderator(email,password):
    """
    Команда создать модератора
    """
    user = get_user_model().objects.create_user(email, password, is_verified=True)
    set_group_user(user, GROUP_MODERATOR)
    return user


def cmd_create_buyer(email,password):
    """
    Команда создать покупателя
    """
    user = get_user_model().objects.create_user(email, password, is_verified=True)
    set_group_user(user, GROUP_BUYER)
    return user
