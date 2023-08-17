from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'max_discount',
        'sale_start',
        'sale_end',
        'goods_on_page',
        'max_file_size',
        'send_bill',
        'send_goods_list',
    ]

    list_display_links = [
        'max_discount',
        'sale_start',
        'sale_end',
        'goods_on_page',
        'max_file_size',
        'send_bill',
        'send_goods_list',
    ]

    change_list_template = 'admin_settings_change_list.jinja2' # добавление кнопок сброса кэша в админке на странице настроек