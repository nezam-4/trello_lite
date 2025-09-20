from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Board, BoardMembership, BoardInvitation, BoardActivity


class BoardMembershipInline(admin.TabularInline):
    model = BoardMembership
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'response_at')
    fields = ('user', 'role', 'status', 'invited_by', 'response_at')


class BoardInvitationInline(admin.TabularInline):
    model = BoardInvitation
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'token', 'is_expired')
    fields = ('invited_email', 'role', 'status', 'invited_by', 'expires_at', 'is_used')


class BoardActivityInline(admin.TabularInline):
    model = BoardActivity
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('action', 'user', 'description', 'created_at')
    ordering = ('-created_at',)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_public', 'active_members_count', 'created_at')
    list_filter = ('is_public', 'created_at', 'color')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'active_members_count')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'owner')
        }),
        (_('Appearance'), {
            'fields': ('color', 'is_public')
        }),
        (_('Statistics'), {
            'fields': ('active_members_count',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    inlines = [BoardMembershipInline, BoardInvitationInline, BoardActivityInline]
    
    def active_members_count(self, obj):
        return obj.active_members_count
    active_members_count.short_description = _('Active Members Count')


@admin.register(BoardMembership)
class BoardMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'board', 'role', 'status', 'invited_by', 'created_at')
    list_filter = ('role', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'board__title', 'invited_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('board', 'user', 'role', 'status')
        }),
        (_('Invitation Info'), {
            'fields': ('invited_by', 'response_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BoardInvitation)
class BoardInvitationAdmin(admin.ModelAdmin):
    list_display = ('invited_email', 'board', 'role', 'status', 'invited_by', 'is_expired', 'created_at')
    list_filter = ('role', 'status', 'is_used', 'created_at')
    search_fields = ('invited_email', 'board__title', 'invited_by__username', 'token')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'token', 'is_expired')
    
    fieldsets = (
        (None, {
            'fields': ('board', 'invited_email', 'role', 'status')
        }),
        (_('Invitation Details'), {
            'fields': ('invited_by', 'description', 'user')
        }),
        (_('Token & Expiry'), {
            'fields': ('token', 'expires_at', 'is_used', 'is_expired')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = _('Expired')


@admin.register(BoardActivity)
class BoardActivityAdmin(admin.ModelAdmin):
    list_display = ('board', 'action', 'user', 'description', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('board__title', 'user__username', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('board', 'action', 'user')
        }),
        (_('Details'), {
            'fields': ('description',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
