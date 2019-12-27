from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .constants import UserType
from django.contrib.auth.models import AbstractUser
from gymnasium.models import Package, Equipmenttype

# Create your models here.

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    school = models.CharField(
        max_length=100, help_text="Enter the School Name", verbose_name="School Name"
    )
    """reg_no_regex"""
    user.username = RegexValidator(
        regex="^[1-9][0-9][A-Z]{3}[0-9]{4}$", message="Should be of format: 18BCE1001"
    )
    equipment_choices = list(Equipmenttype.objects.all())
    equipment_interest = models.CharField(max_length=100, choices=equipment_choices, default=None)

    package_choices = list(Package.objects.all())
    package_interest = models.CharField(max_length=100, choices=package_choices, default=None)

    class Meta:
        verbose_name = "student"
        verbose_name_plural = "students"

    def __str__(self):
        return "{} ({})".format(str(self.user), str(self.school))

class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    emp_id_regex = RegexValidator(
        regex="^[0-9]{5}$", message="Should be of format: 12345", code="invalid_number"
    )

    class Meta:
        verbose_name = "trainer"
        verbose_name_plural = "trainers"

    def __str__(self):
        return "{} ({})".format(str(self.user), str(self.school))

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    emp_id_regex = RegexValidator(
        regex="^[0-9]{5}$", message="Should be of format: 12345", code="invalid_number"
    )

    class Meta:
        verbose_name = "manager"
        verbose_name_plural = "managers"

    def __str__(self):
        return "{} ({})".format(str(self.user), str(self.school))



class Attendence(models.Model) :
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, primary_key=True)
    date = models.DateField()