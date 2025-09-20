from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Task, TaskComment


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('user', 'content', 'created_at')
    ordering = ('-created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'list', 'created_by', 'priority', 'due_date', 'is_completed', 'is_overdue', 'position', 'created_at')
    list_filter = ('priority', 'is_completed', 'due_date', 'list__board', 'created_at')
    search_fields = ('title', 'description', 'list__title', 'list__board__title', 'created_by__username')
    ordering = ('list', 'position', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'is_overdue', 'board')
    filter_horizontal = ('assigned_to',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'list', 'created_by')
        }),
        (_('Assignment & Priority'), {
            'fields': ('assigned_to', 'priority', 'position')
        }),
        (_('Schedule'), {
            'fields': ('due_date', 'is_overdue')
        }),
        (_('Status'), {
            'fields': ('is_completed', 'completed_at')
        }),
        (_('Related'), {
            'fields': ('board',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    inlines = [TaskCommentInline]
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = _('Overdue')
    
    def board(self, obj):
        return obj.board
    board.short_description = _('Board')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('list', 'list__board', 'created_by').prefetch_related('assigned_to')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'content_preview', 'created_at')
    list_filter = ('task__list__board', 'created_at')
    search_fields = ('content', 'task__title', 'user__username', 'task__list__title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('task', 'user', 'content')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('Content Preview')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'user', 'task__list')
