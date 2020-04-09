from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import EquipmentForm, NotificationForm
from users.models import CustomUser, CustomerProfile
from .models import Membership, Package, Notification, Equipmenttype, Announcement
import datetime

def HomePage(request) :
    return render(request, 'gymnasium/home.html')


def FitnessClasses(request) :
    return render(request, 'gymnasium/fitnessClasses.html')


def Aquatics(request) :
    return render(request, 'gymnasium/aquatics.html')


"""@login_required
def AddEquipment(request) :
    if request.method == 'POST':  # data sent by user
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()  # this will save the details to database
            return HttpResponse('Project details added to database')
    else:  # display empty form
        form = EquipmentForm()
    return render(request, 'Manager/addEquipment.html', {'add_eqip_form' : form})"""


@login_required
def DisplayCustomerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
    customer_profile_object = CustomerProfile.objects.get(account=user_object)
    membership_object = Membership.objects.get(name=user_object)
    membership_deadline = membership_object.deadline
    membership_deadline = membership_deadline.replace(tzinfo=None)
    if membership_deadline >= datetime.datetime.now(tz=None) :
        membership_status = "Active"
    else :
        membership_status = "Inactive"
    return render(request, 'Customer/profile.html', {'customer' : customer_profile_object, 'membership_status' : membership_status, 'membership' : membership_object})


@login_required
def ChangeCustomerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
    customer_profile_object = CustomerProfile.objects.get(account=user_object)
    if request.method == 'POST' :
        user_object.email = request.POST['email']
        customer_profile_object.mobile = request.POST['mobile']
        customer_profile_object.address = request.POST['address']
        customer_profile_object.age = request.POST['age']
        customer_profile_object.weight = request.POST['weight']
        customer_profile_object.medical_history = request.POST['medical_history']
        customer_profile_object.allergies = request.POST['allergies']
        # Recieve all the names of the selected options from the checkbox, get their objects and pass them to the set() method of the respective object.
        interested_equipments = request.POST.getlist('equipment')
        equipment_id_list = []
        for equipment_name in interested_equipments :
            equipment_id_list.append(Equipmenttype.objects.get(name=equipment_name))
        customer_profile_object.equipment_interest.set(equipment_id_list)
        # Saving the modified objects
        user_object.save()
        customer_profile_object.save()
        messages.success(request, 'Details entered have been updated.')
        return redirect('/customer-profile')
    else :
        equipment_types = Equipmenttype.objects.all()
        return render(request, 'Customer/updateCustomer.html', {'customer' : customer_profile_object, 'equipment_types' : equipment_types})
    

@login_required
def changePassword(request) :
    # Choose the base template for different types of users.
    if request.user.is_customer :
        base_template = 'Customer/base.html'
    elif request.user.is_trainer :
        base_template = 'Trainer/base.html'
    else :
        base_template = 'Manager/base.html'
    # Handle Form Request.
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/customer-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/changePassword.html', {
        'form': form,
        'base_template' : base_template
    })


@login_required
def DisplayNotification(request) :
    # To delete the expired notifications from the database
    Notification.objects.filter(end_date__lt=datetime.date.today()).delete()
    # To display the active notifications
    user_object = CustomUser.objects.get(username=request.user)
    customer_profile_object = CustomerProfile.objects.get(account=user_object)
    gym_class_object = customer_profile_object.gym_class
    notification_objects = Notification.objects.filter(gym_class=gym_class_object)
    num_notifications = len(notification_objects)
    context = {'num_notifications' : num_notifications, 'notifications' : notification_objects}
    if user_object.is_customer :
        membership_object = Membership.objects.get(name=user_object)
        membership_deadline = membership_object.deadline
        membership_deadline = membership_deadline.replace(tzinfo=None)
        days_left = (membership_deadline - datetime.datetime.now(tz=None)).days
        if days_left < 10 and days_left >= 0 :
            context['membership_deadline_near'] = True
            context['days_left_expiry'] = days_left
        else :
            context['membership_deadline_near'] = False
    return render(request, 'Customer/displayNotification.html', context)


"""def PostNotification(request) :
    if request.method == 'POST' :
        form = NotificationForm(request.POST)
        if form.is_valid() :
            form.save()
    else :
        form = NotificationForm()
    return render(request, 'Manager/postNotification.html', {'new_notification_form' : form})"""


def DisplayAnnouncements(request) :
    Announcement.objects.filter(end_date__lt=datetime.date.today()).delete()
    announcement_objects = Announcement.objects.all()
    num_announcements = len(announcement_objects)
    context = {'num_announcements' : num_announcements, 'announcements' : announcement_objects}
    return render(request, 'gymnasium/announcement.html', context)