from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')  

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True, validators=[alphanumeric])
    password = models.CharField(max_length=30, validators=[alphanumeric])
    email = models.EmailField(max_length=254, unique=True)
    def __str__(self):
        return (f"{self.username} {self.email}")

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.CharField(max_length=140)
    created_at = models.DateTimeField()
    edited_at = models.DateTimeField(blank = True, default = None)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return (f"{self.user}   {self.post}   {self.created_at}   {str(self.edited_at)}   {str(self.likes)}")


class Followers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ManyToManyField(User, related_name='follower')

    def __str__(self):
        return (f"{self.user} {self.follower}")
        
class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='liked_post')
    
    def __str__(self):
        return (f"{self.user} {self.post}")
