from django.contrib import admin
from .models import Equipment, AMC, Equipmenttype, Package, Membership, Notification

admin.site.register(Equipment)
admin.site.register(AMC)
admin.site.register(Equipmenttype)
admin.site.register(Package)
admin.site.register(Membership)
admin.site.register(Notification)