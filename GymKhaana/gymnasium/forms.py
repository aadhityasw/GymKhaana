from django.forms import ModelForm
from .models import Equipment, Notification

class EquipmentForm(ModelForm) :
    class Meta :
        model = Equipment
        exclude = ()


class NotificationForm(ModelForm) :
    class Meta :
        model = Notification
        exclude = ()