from django.contrib import admin
from .models import List, UserProfile

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_public', 'created_at', 'updated_at')
    list_filter = ('is_public', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'content', 'tags')
    raw_id_fields = ('owner', 'original_list')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')
