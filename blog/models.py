from django.db import models
from user.models import CustomUser  

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="posts")  
    date_posted = models.DateField()
    image_url = models.URLField(default='https://via.placeholder.com/300x150')

    def __str__(self):
        return self.title

    def get_image_url(self):
        return self.image_url

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
