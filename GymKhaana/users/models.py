from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from gymnasium.models import Equipmenttype

class CustomUserManager(UserManager) :
    pass

class CustomUser(AbstractUser) :
    is_customer = models.BooleanField(default=True)
    is_manager = models.BooleanField(default=False)
    is_trainer = models.BooleanField(default=False)

    objects = CustomUserManager()

    def __str__(self):
        return (self.username)


class CustomerProfile(models.Model) :
    account = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="profile")
    medical_history = models.TextField(max_length=1000)
    age = models.IntegerField(null=False, blank=False)
    weight = models.IntegerField(null=False, blank=False)
    allergies = models.TextField(max_length=500)
    address = models.TextField(max_length=500)
    gym_package = models.ForeignKey('gymnasium.Package', on_delete=models.CASCADE, related_name="subscribed_package")
    equipment_interest = models.ManyToManyField(Equipmenttype, related_name="equipment_interest")

    def __str__(self):
        return str(self.account.username)