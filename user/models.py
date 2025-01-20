from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import re


def validate_username(value):
    regex = r'^[a-zA-Z0-9@.+_\- ]+$'
    if not re.match(regex, value):
        raise ValidationError(
            "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters, and spaces."
        )


def validate_password(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', value):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', value):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'\d', value):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r'[@$!%*?&]', value):
        raise ValidationError("Password must contain at least one special character (@$!%*?&).")


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True) 
    REQUIRED_FIELDS = ['email']

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_username],
    )

    image = models.URLField(
        max_length=500,
        blank=True,
        default='',  # Default value can be set later in the save method
    )
    
    about_me = models.TextField(
        blank=True,
        default="About me has not been written yet."
    )

    def clean(self):
        super().clean()
        validate_password(self.password)
        # Ensure unique email, excluding the current instance
        if CustomUser.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError("An account with this email already exists. Please use a different email.")

    def __str__(self):
        return self.username

    def get_image_url(self):
        return f"https://ui-avatars.com/api/?name={self.username.replace(' ', '+')}&background=random"

    def save(self, *args, **kwargs):
        # Set default image URL if not already set
        if not self.image:
            self.image = self.get_image_url()
        super().save(*args, **kwargs)
