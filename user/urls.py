from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('profile/', user_profile, name='user-profile'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('request-password-reset/', request_password_reset, name='request_password_reset'),
    path('reset-password/', reset_password, name='reset_password'),
    path('update-profile/', update_user_profile, name='update_user_profile'),
]
