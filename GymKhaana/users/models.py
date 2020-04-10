from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from gymnasium.models import Equipmenttype

class CustomUserManager(UserManager) :
    pass

class CustomUser(AbstractUser) :
    role_choices = [('C', 'Customer'), ('T', 'Trainer'), ('M', 'Manager'), ('A', 'Administrator')]
    role = models.CharField(max_length=1, choices=role_choices, default='C')
    objects = CustomUserManager()

    def __str__(self):
        return (self.username)


class CustomerProfile(models.Model) :
    account = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="profile", limit_choices_to={'role' : 'C'})
    full_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Full Name", default='-')
    mobile = models.IntegerField(null=False, blank=False)
    medical_history = models.TextField(max_length=1000, blank=False)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='O')
    age = models.IntegerField(null=False, blank=False)
    weight = models.IntegerField(null=False, blank=False)
    allergies = models.TextField(max_length=500)
    address = models.TextField(max_length=500)
    gym_package = models.ForeignKey('gymnasium.Package', on_delete=models.CASCADE, related_name="subscribed_package")
    gym_class = models.ForeignKey('gymnasium.GymClass', on_delete=models.CASCADE, related_name="registered_class", null=True, blank=True)
    equipment_interest = models.ManyToManyField(Equipmenttype, related_name="equipment_interest")

    def __str__(self):
        return str(self.full_name)


class ManagerProfile(models.Model) :
    account = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="manager_profile_account", limit_choices_to={'role' : 'M'})
    full_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Full Name", default='-')
    mobile = models.IntegerField(null=False, blank=False)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='O')
    address = models.TextField(max_length=500)
    age = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return str(self.full_name)


class TrainerProfile(models.Model) :
    account = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="trainer_profile_account", limit_choices_to={'role' : 'T'})
    full_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Full Name", default='-')
    mobile = models.IntegerField(null=False, blank=False)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='O')
    address = models.TextField(max_length=500)
    age = models.IntegerField(null=False, blank=False)
    medical_history = models.TextField(max_length=1000, blank=True)
    gym_class = models.ForeignKey('gymnasium.GymClass', on_delete=models.CASCADE, related_name="allocated_class", null=True, blank=True)

    def __str__(self):
        return str(self.full_name)