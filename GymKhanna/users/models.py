from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser) :
    isStudent = models.BooleanField(default=True)
    isManager = models.BooleanField(default=False)
    isTrainer = models.BooleanField(default=False)

    def __str__(self):
        return self.username