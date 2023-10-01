from django.contrib import admin
from histviewapp.models import HistoryViewed


@admin.register(HistoryViewed)
class MyHistoryViewed(admin.ModelAdmin):
    list_display = ('user', 'product', 'watched_at', )
    search_fields = ['user', 'product', ]
