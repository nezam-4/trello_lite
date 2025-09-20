from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import List


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'position', 'color', 'tasks_count', 'created_at')
    list_filter = ('color', 'board', 'created_at')
    search_fields = ('title', 'board__title', 'board__owner__username')
    ordering = ('board', 'position', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'tasks_count')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'board', 'position')
        }),
        (_('Appearance'), {
            'fields': ('color',)
        }),
        (_('Statistics'), {
            'fields': ('tasks_count',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def tasks_count(self, obj):
        return obj.tasks_count
    tasks_count.short_description = _('Tasks Count')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('board')
