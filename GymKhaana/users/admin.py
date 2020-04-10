from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm 
from .models import CustomUser, CustomerProfile, TrainerProfile, ManagerProfile


class CustomUserAdmin(UserAdmin):
    model = CustomUser 
    add_form = CustomUserCreationForm 
    form = CustomUserChangeForm 
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomerProfile)
admin.site.register(TrainerProfile)
admin.site.register(ManagerProfile)