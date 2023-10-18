from django.contrib import admin
from django.core.cache import cache
from django.shortcuts import render
from django.urls import path

from .models import SiteSettings, ImportLog


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    # добавление кнопок сброса кэша в админке на странице настроек
    change_list_template = "admin_settings/admin_settings_change_list.html"

    list_display = [
        "max_discount",
        "cache_time",
        "banner_time",
        "goods_on_page",
        "max_file_size",
    ]

    list_display_links = [
        "max_discount",
        "cache_time",
        "banner_time",
        "goods_on_page",
        "max_file_size",
    ]


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'import_id', 'timestamp', 'level', 'message']
    list_display_links = ['id', 'user', 'import_id']
    search_fields = ['timestamp', 'import_id']
    list_filter = ['user', 'level', 'import_id']
    ordering = ["timestamp"]
