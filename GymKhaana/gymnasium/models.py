from django.db import models
from django.utils import timezone

class Equipmenttype(models.Model) :
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Equipment(models.Model) :
    name = models.CharField(max_length=200)
    date_of_purchase = models.DateField()
    equipment_type = models.ForeignKey(Equipmenttype, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipments"

    def __str__(self):
        return self.name


class AMC(models.Model) :
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    start_date = models.DateField()
    renewal_date = models.DateField()

    class Meta:
        verbose_name = "AMC"
        verbose_name_plural = "AMC"

    def __str__(self):
        return self.equipment.name


class Package(models.Model) :
    name = models.CharField(max_length=200)
    price = models.FloatField(max_length=4)
    duration = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Package"
        verbose_name_plural = "Packages"

    def __str__(self):
        stri = self.name + " - " + str(self.duration) + " months"
        return (stri)


class GymClass(models.Model) :
    name = models.CharField(max_length=200)
    package_name = models.ForeignKey('Package', on_delete=models.CASCADE, related_name="gym_class_for_package")
    timings = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Gym class"
        verbose_name_plural = "Gym classes"

    def __str__(self):
        stri = self.name + " - " + str(self.package_name.name)
        return (stri)


class Membership(models.Model) :
    name = models.ForeignKey(
        'users.CustomUser', 
        on_delete=models.CASCADE, 
        related_name="customer_membership",
        limit_choices_to={'role' : 'C'})
    deadline = models.DateTimeField()
    package = models.ForeignKey('Package', on_delete=models.CASCADE, related_name="membership_for_package")
    gym_class = models.ForeignKey('GymClass', on_delete=models.CASCADE, related_name="membership_for_gym_class")

    class Meta :
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"

    def __str__(self):
        return_string = str(self.name) + " - " + str(self.package)
        return (return_string)


class Notification(models.Model) :
    gym_class = models.ManyToManyField(GymClass, related_name="notification_for_gym_class")
    author = models.ForeignKey(
        'users.CustomUser', 
        on_delete=models.CASCADE, 
        related_name="trainer", 
        limit_choices_to=
            models.Q(role='T') | models.Q(role='M') | models.Q(role='A')
        )
    content = models.TextField(max_length=500)
    # end_date = models.DateField(verbose_name="Expiry for Notification")
    expiry = models.DateTimeField(verbose_name="Expiry for Notification", default=timezone.now)

    class Meta :
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return (str(self.id))


class Announcement(models.Model) :
    account = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role' : 'M'})
    content = models.TextField(max_length=500)
    end_date = models.DateField(verbose_name="Expiry for Notification")

    class Meta :
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"

    def __str__(self):
        return (str(self.account))