from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'about_me']  # Customize columns in the list view
    search_fields = ['username', 'email']  # Add a search bar
    fieldsets = (
        ('User Info', {'fields': ('username', 'email', 'about_me','image')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
