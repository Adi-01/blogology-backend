from rest_framework import serializers
from .models import Post
from user.models import CustomUser  

class UserSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'image','email']

    def get_image_url(self, obj):
        return obj.get_image_url()


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True) 

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'date_posted', 'image_url']

    def create(self, validated_data):
        user = self.context['request'].user
        post = Post.objects.create(author=user, **validated_data)
        return post
