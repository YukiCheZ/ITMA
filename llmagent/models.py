from django.db import models
from django.contrib.auth.models import User

class APIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 与用户关联
    api_key = models.CharField(max_length=255)  # 存储API Key

    def __str__(self):
        return f"API Key for {self.user.username}"