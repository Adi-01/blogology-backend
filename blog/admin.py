from django.contrib import admin
from .models import Post, Comment
from django.utils.html import format_html


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_posted', 'image_url_preview')
    list_filter = ('date_posted', 'author')
    search_fields = ('title', 'content', 'author__username')
    ordering = ('-date_posted',)
    readonly_fields = ('image_url_preview',)
    
    def image_url_preview(self, obj):
        """Display the image in the admin panel."""
        return format_html(f'<img src="{obj.image_url}" width="150" height="75" />')
    image_url_preview.short_description = "Image Preview"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'date_posted','id')
    list_filter = ('date_posted', 'author')
    search_fields = ('post__title', 'author__username')
    ordering = ('-date_posted',)
