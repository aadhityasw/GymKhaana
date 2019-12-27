from django.contrib import admin
from .models import Equipment, AMC, Equipmenttype, Package
# Register your models here.

admin.site.register(Equipment)
admin.site.register(AMC)
admin.site.register(Equipmenttype)
admin.site.register(Package)