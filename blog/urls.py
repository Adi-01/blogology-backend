from django.urls import path
from blog import views

urlpatterns = [
    path('posts/', views.post_list),
    path('posts/<int:pk>/', views.post_detail),
    path('posts/create/', views.create_post),
    # path("posts/by-user/", views.get_user_posts, name="get_user_posts"),
    path('posts/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:pk>/comments/', views.get_comments, name='get_comments'),
    path('posts/<int:pk>/comments/add/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    # path('posts/user/<int:user_id>/', views.get_posts_by_user, name='get-posts-by-user'),
]
