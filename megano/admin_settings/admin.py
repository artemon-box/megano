from django.contrib import admin
from django.core.cache import cache
from django.shortcuts import render
from django.urls import path

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    change_list_template = 'admin_settings/admin_settings_change_list.html'  # добавление кнопок сброса кэша в админке на странице настроек

    list_display = [
        'max_discount',
        'cache_time',
        'banner_time',
        'goods_on_page',
        'max_file_size',
    ]

    list_display_links = [
        'max_discount',
        'cache_time',
        'banner_time',
        'goods_on_page',
        'max_file_size',
    ]
