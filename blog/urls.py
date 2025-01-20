from django.urls import path
from blog import views

urlpatterns = [
    path('posts/', views.post_list),
    path('posts/<int:pk>/', views.post_detail),
    path('posts/create/', views.create_post),
    path("posts/by-user/", views.get_user_posts, name="get_user_posts"),
    path('posts/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
]
