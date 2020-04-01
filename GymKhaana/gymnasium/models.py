from django.db import models
#from users.models import CustomUser;

class Equipmenttype(models.Model) :
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Equipment(models.Model) :
    name = models.CharField(max_length=200)
    date_of_purchase = models.DateField()
    equipment_type = models.ForeignKey(Equipmenttype, on_delete=None)

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
    timings = models.CharField(max_length=100)
    duration = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Package"
        verbose_name_plural = "Packages"

    def __str__(self):
        stri = self.name + " - " + str(self.duration) + " months"
        return (stri)


class Membership(models.Model) :
    name = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name="customer")
    deadline = models.DateTimeField()
    package = models.ForeignKey('Package', on_delete=models.CASCADE, related_name="package")

    class Meta :
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"

    def __str__(self):
        return_string = str(self.name) + " - " + str(self.package)
        return (return_string)


class Notification(models.Model) :
    #customer = models.ManyToManyField(CustonUser, related_name="customers")
    package = models.ManyToManyField(Package, related_name="packages")
    trainer = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name="trainer")
    content = models.TextField(max_length=500)
    end_time = models.DurationField()

    class Meta :
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return (str(self.trainer))