from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'id', 'email', 'about_me', 'followers_count']  # Add followers fields
    search_fields = ['username', 'email']  # Add a search bar

    fieldsets = (
        ('User Info', {'fields': ('username', 'email', 'about_me', 'image')}),
        ('Followers Info', {
            'fields': ('followers_count', 'followers_list'),  # Add followers fields here
            'classes': ('collapse',),  # Optional: make this section collapsible
        }),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    readonly_fields = ['followers_count', 'followers_list']  # Make these fields read-only

    def followers_count(self, obj):
        return obj.followers.count()  


    followers_count.short_description = 'Followers Count'  # Set column name in admin

    def followers_list(self, obj):
        return ", ".join([f.username for f in obj.followers.all()])  # Assuming CustomUser has a username field



    followers_list.short_description = 'Followers List'  # Set column name in admin