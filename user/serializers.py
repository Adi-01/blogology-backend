from rest_framework import serializers
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError , ObjectDoesNotExist
from .models import CustomUser, validate_password
from blog.serializers import PostSerializer

def validate_email_uniqueness(value, instance=None):
    try:
        django_validate_email(value)
    except DjangoValidationError:
        raise serializers.ValidationError("Enter a valid email address.")

    query = CustomUser.objects.filter(email=value)
    if instance:
        query = query.exclude(pk=instance.pk)
    if query.exists():
        raise serializers.ValidationError("This email is already in use.")
    return value

#Creating the User for serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'image', 'about_me' ]
        extra_kwargs = {
            'password': {'write_only': True},
            'image': {'read_only': True},
            'about_me':{'read_only': True}
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        return validate_email_uniqueness(value)

    def create(self, validated_data):
        self.validate_email(validated_data.get('email'))
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

#User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True)
    post_count = serializers.SerializerMethodField(read_only=True)
    posts = PostSerializer(many=True, read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    followers_list = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'image', 'date_joined','about_me', 'post_count', 'posts', 'followers_count', 'followers_list', 'is_following']
        extra_kwargs = {
            'about_me': {'read_only': True},
        }
        
    def get_post_count(self, obj):
        return obj.posts.count()
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    

    def get_followers_list(self, obj):
        return [f.username for f in obj.followers.all()]
    
    def get_is_following(self, obj):
        request = self.context.get('request', None)
        if not request or not hasattr(request, 'user'):
            return False  # 🚨 Skip if no request
        
        user = request.user
        if user.is_anonymous:  # 🔥 Handle AnonymousUser
            return False

        if user == obj:
            return False

        
        return user in obj.followers.all()



#User Profile Update Serializer
class UserProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'image','about_me']
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False},
            'image': {'required': False},
            'about_me': {'required': False},
        }

    def validate_email(self, value):
        return validate_email_uniqueness(value, self.instance)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

#Password reset request:
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check if a user exists with the provided email
        try:
            CustomUser.objects.get(email=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("No user found with this email.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(
        min_length=8, 
        max_length=128, 
        validators=[validate_password]
    )

    def validate_new_password(self, value):
        validate_password(value)
        return value