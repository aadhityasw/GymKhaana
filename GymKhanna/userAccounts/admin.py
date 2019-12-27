from django.contrib import admin
from .models import Trainer, Student, Manager

admin.site.register(Manager)
admin.site.register(Trainer)
admin.site.register(Student)
