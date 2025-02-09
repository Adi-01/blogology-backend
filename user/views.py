from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from .serializers import UserSerializer,UserProfileSerializer,PasswordResetRequestSerializer, PasswordResetSerializer, UserProfileUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
from django.shortcuts import get_object_or_404
from django.core.cache import cache

@api_view(['POST'])
@permission_classes([AllowAny]) 
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully!"}, status=HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user) 
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Fetch the profile details of the authenticated user."""
    cache_key = f'user_profile_{request.user.id}'
    profile = cache.get(cache_key)  # Try to get the cached profile
    
    if not profile:  # If not cached, fetch from the database
        profile = UserProfileSerializer(request.user, context={'request': request}).data
        cache.set(cache_key, profile, timeout=60 * 15)  # Cache for 15 minutes
    
    return Response(profile, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Respond with a generic message to avoid user enumeration
            return Response(
                {"detail": "If the email exists, a password reset link will be sent."},
                status=status.HTTP_200_OK,
            )

        # Generate the token
        token = default_token_generator.make_token(user)

        # Create the frontend reset password URL
        reset_link = f"{settings.FRONTEND_URL}reset-your-password?token={token}&email={email}"

        try:
            # Send the email using Gmail
            send_mail(
                subject="Password Reset Request",
                message=f"Hi {user.username},\n\nClick the link below to reset your password:\n\n{reset_link}\n\nIf you didn't request this, please ignore this email.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )
            return Response(
                {"detail": "If the email exists, a password reset link will be sent."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Failed to send password reset email: {e}")
            return Response(
                {"error": "Failed to send email. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = request.data['email']
        token = request.data['token']
        new_password = serializer.validated_data['new_password']

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Retrieve or update the authenticated user's profile (username, email, image)."""
    user = request.user

    # Handle GET request to retrieve the user's profile data
    if request.method == 'GET':
        cache_key = f'user_profile_{user.id}'
        profile = cache.get(cache_key)  # Try to get the cached profile
        
        if not profile:  # If not cached, fetch from the database
            profile = UserProfileSerializer(user, context={'request': request}).data
            cache.set(cache_key, profile, timeout=60 * 15)  # Cache for 15 minutes
        
        return Response(profile, status=status.HTTP_200_OK)

    # Handle PATCH request to update the user's profile data
    elif request.method == 'PATCH':
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            # Invalidate the cache for the user's profile
            cache_key = f'user_profile_{user.id}'
            cache.delete(cache_key)  # Remove the cached profile
            
            # Optionally, you can return the updated profile data
            updated_profile = UserProfileSerializer(user, context={'request': request}).data
            return Response(updated_profile, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_specific_user_profile(request, user_id):
    """Retrieve a specific user's profile."""
    cache_key = f'user_profile_{user_id}'
    profile = cache.get(cache_key)  # Try to get the cached profile
    
    if not profile:  # If not cached, fetch from the database
        try:
            user = CustomUser.objects.get(pk=user_id)
            profile = UserProfileSerializer(user, context={'request': request}).data
            cache.set(cache_key, profile, timeout=60 * 15)  # Cache for 15 minutes
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(profile, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(CustomUser, id=user_id)
    current_user = request.user

    if user_to_follow == current_user:
        return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    if current_user in user_to_follow.followers.all():
        return Response({"detail": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

    user_to_follow.followers.add(current_user)

    return Response({
        "detail": f"You are now following {user_to_follow.username}.",
        "is_following": True,  # ✅ Send updated state
        "followers_count": user_to_follow.followers.count()  # ✅ Send updated count
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
    current_user = request.user

    if user_to_unfollow == current_user:
        return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    if current_user not in user_to_unfollow.followers.all():
        return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

    user_to_unfollow.followers.remove(current_user)

    return Response({
        "detail": f"You have unfollowed {user_to_unfollow.username}.",
        "is_following": False,  # ✅ Send updated state
        "followers_count": user_to_unfollow.followers.count()  # ✅ Send updated count
    }, status=status.HTTP_200_OK)


