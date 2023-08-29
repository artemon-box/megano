from django.contrib import admin
from .models import SiteSettings


# @admin.register(SiteSettings)
# class SiteSettingsAdmin(admin.ModelAdmin):
#     list_display = [
#         'max_discount',
#         'cache_time',
#         'banner_time',
#         'sale_start',
#         'sale_end',
#         'goods_on_page',
#         'max_file_size',
#     ]
#
#     list_display_links = [
#         'max_discount',
#         'cache_time',
#         'banner_time',
#         'sale_start',
#         'sale_end',
#         'goods_on_page',
#         'max_file_size',
#     ]

    # change_list_template = 'admin_settings_change_list.html'  # добавление кнопок сброса кэша в админке на странице настроек
