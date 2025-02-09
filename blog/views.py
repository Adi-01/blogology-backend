from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from django.utils import timezone
from django.core.cache import cache


@api_view(['GET'])
@permission_classes([AllowAny])
def post_list(request):
    """
    List all posts.
    """
    cache_key = 'post_list'  # Define a cache key for the list of posts
    posts = cache.get(cache_key)  # Try to get the cached data
    
    if not posts:  # If not cached, fetch from the database
        posts = Post.objects.all()
        cache.set(cache_key, posts, timeout=60 * 15)  # Cache for 15 minutes
    
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def post_detail(request, pk):
    """
    Retrieve a specific post.
    """
    cache_key = f'post_detail_{pk}'  # Define a cache key for the specific post
    post = cache.get(cache_key)  # Try to get the cached data
    
    if not post:  # If not cached, fetch from the database
        try:
            post = Post.objects.get(pk=pk)
            cache.set(cache_key, post, timeout=60 * 15)  # Cache for 15 minutes
        except Post.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PostSerializer(post)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    #Adding the current date:
    data = request.data.copy()
    data['date_posted'] = timezone.now().date()

    # Serialize the data and create the post
    serializer = PostSerializer(data=data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        cache.delete('post_list')
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return the post data with the author info
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_comments(request, pk):
    comments = Comment.objects.filter(post_id=pk)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

# View to add a comment to a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, pk):
    data = request.data
    data['post'] = pk
    data['author'] = request.user.id
    

    serializer = CommentSerializer(data=data, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to delete a comment
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user != comment.author:  # Ensure the user is the author of the comment
        return Response({"detail": "You don't have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def edit_post(request, pk):
    cache_key = f'post_detail_{pk}'  # Define a cache key for the specific post

    if request.method == 'GET':
        # Try to get the cached post
        post = cache.get(cache_key)
        
        if not post:  # If not cached, fetch from the database
            try:
                post = Post.objects.get(pk=pk)
                cache.set(cache_key, post, timeout=60 * 15)  # Cache for 15 minutes
            except Post.DoesNotExist:
                return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post)
        return Response(serializer.data)

    if request.method == 'PUT':
        # Handle the PUT request to update the post
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the logged-in user is the author of the post
        if post.author != request.user:
            return Response({"detail": "You can only edit your own posts."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostSerializer(post, data=request.data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            # Invalidate the cache for the post
            cache.delete(cache_key)  # Remove the cached post
            cache.delete('post_list')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, pk):
    cache_key = f'post_detail_{pk}'  # Define a cache key for the specific post

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    # Ensure the logged-in user is the author of the post
    if post.author != request.user:
        return Response({"detail": "You can only delete your own posts."}, status=status.HTTP_403_FORBIDDEN)

    post.delete()
    # Invalidate the cache for the post
    cache.delete(cache_key)  # Remove the cached post
    cache.delete('post_list')
    return Response({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)