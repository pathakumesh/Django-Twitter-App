from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    dob = models.DateField(blank=False)


class Post(models.Model):
    text = models.CharField(max_length=100, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.text


class Likes(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('liked_at',)

    def __str__(self):
        return self.user


class UserFollowing(models.Model):
    user_id = models.ForeignKey(User, related_name="following",
                                on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(User, related_name="followers",
                                          on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ("user_id", "following_user_id")
        ordering = ('created_at',)

    def __str__(self):
        f"{self.user_id} follows {self.following_user_id}"
