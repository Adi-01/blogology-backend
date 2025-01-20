from django.db import models
from user.models import CustomUser  # Import the CustomUser model

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Use CustomUser as the author
    date_posted = models.DateField()
    image_url = models.URLField(default='https://via.placeholder.com/300x150')

    def __str__(self):
        return self.title

    def get_image_url(self):
        return self.image_url
