from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class CustomUserManager(UserManager) :
    pass

class CustomUser(AbstractUser) :
    is_student = models.BooleanField(default=True)
    is_manager = models.BooleanField(default=False)
    is_trainer = models.BooleanField(default=False)

    objects = CustomUserManager()

    def __str__(self):
        return self.username