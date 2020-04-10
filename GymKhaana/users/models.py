from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from gymnasium.models import Equipmenttype

class CustomUserManager(UserManager) :
    pass

class CustomUser(AbstractUser) :
    is_customer = models.BooleanField(default=True)
    is_manager = models.BooleanField(default=False)
    is_trainer = models.BooleanField(default=False)
    role_choices = [('S', 'Student'), ('T', 'Trainer'), ('M', 'Manager'), ('A', 'Administrator')]
    role = models.CharField(max_length=1, choices=role_choices, default='S')
    objects = CustomUserManager()

    def __str__(self):
        return (self.username)


class CustomerProfile(models.Model) :
    account = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="profile", limit_choices_to={'is_customer' : True})
    full_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Full Name", default='-')
    mobile = models.IntegerField(null=False, blank=False)
    medical_history = models.TextField(max_length=1000)
    age = models.IntegerField(null=False, blank=False)
    weight = models.IntegerField(null=False, blank=False)
    allergies = models.TextField(max_length=500)
    address = models.TextField(max_length=500)
    gym_package = models.ForeignKey('gymnasium.Package', on_delete=models.CASCADE, related_name="subscribed_package")
    gym_class = models.ForeignKey('gymnasium.GymClass', on_delete=models.CASCADE, related_name="registered_class")
    equipment_interest = models.ManyToManyField(Equipmenttype, related_name="equipment_interest")

    def __str__(self):
        return str(self.full_name)


"""class ManagerProfile(models.Model) :
    account = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="profile", limit_choices_to={'is_manager' : True})
    full_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Full Name", default='-')
    mobile = models.IntegerField(null=False, blank=False)
    address = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return str(self.full_name)


class ManagerProfile(models.Model) :
    account = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="profile", limit_choices_to={'is_trainer' : True})
    full_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Full Name", default='-')
    mobile = models.IntegerField(null=False, blank=False)
    address = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return str(self.full_name)"""