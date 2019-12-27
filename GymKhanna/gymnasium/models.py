from django.db import models

# Create your models here.


class Equipment(models.Model) :
    name = models.CharField(max_length=200)
    date_of_purchase = models.DateField()

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

    class Meta:
        verbose_name = "Package"
        verbose_name_plural = "Packages"

    def __str__(self):
        return self.equipment.name