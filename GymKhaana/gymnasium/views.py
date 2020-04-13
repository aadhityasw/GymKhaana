from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.db import models

from users.models import CustomUser, CustomerProfile, TrainerProfile, ManagerProfile
from .models import Membership, Package, Notification, Equipmenttype, Announcement, GymClass
import datetime


# General Website Pages


def HomePage(request) :
    return render(request, 'gymnasium/home.html')


def FitnessClasses(request) :
    return render(request, 'gymnasium/fitnessClasses.html')


def Aquatics(request) :
    return render(request, 'gymnasium/aquatics.html')


def DisplayAnnouncements(request) :
    Announcement.objects.filter(end_date__lt=datetime.date.today()).delete()
    announcement_objects = Announcement.objects.all()
    num_announcements = len(announcement_objects)
    context = {'num_announcements' : num_announcements, 'announcements' : announcement_objects}
    return render(request, 'gymnasium/announcement.html', context)


@login_required
def changePassword(request) :
    # Choose the base template for different types of users.
    if request.user.role == 'C' :
        base_template = 'Customer/base.html'
    elif request.user.role == 'T' :
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


# Customer Pages


@login_required
def DisplayCustomerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
    """customer_profile_object = CustomerProfile.objects.get(account=user_object)
    membership_object = Membership.objects.get(name=user_object)"""
    customer_profile_object = user_object.customer_profile_account.get()
    membership_object = user_object.customer_membership.get()
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
    """customer_profile_object = CustomerProfile.objects.get(account=user_object)"""
    customer_profile_object = user_object.customer_profile_account.get()
    if request.method == 'POST' :
        user_object.email = request.POST['email']
        customer_profile_object.full_name = request.POST['full_name']
        customer_profile_object.mobile = request.POST['mobile']
        customer_profile_object.address = request.POST['address']
        customer_profile_object.age = request.POST['age']
        customer_profile_object.weight = request.POST['weight']
        customer_profile_object.medical_history = request.POST['medical_history']
        customer_profile_object.allergies = request.POST['allergies']
        customer_profile_object.gender = request.POST['gender']
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
def DisplayCustomerNotification(request) :
    # To delete the expired notifications from the database
    Notification.objects.filter(expiry__lt=datetime.datetime.now()).delete()
    # To display the active notifications
    user_object = CustomUser.objects.get(username=request.user)
    customer_profile_object = CustomerProfile.objects.get(account=user_object)
    gym_class_object = customer_profile_object.gym_class
    notification_objects = Notification.objects.filter(gym_class=gym_class_object)
    num_notifications = len(notification_objects)
    context = {'num_notifications' : num_notifications, 'notifications' : notification_objects}
    if user_object.role == 'C' :
        """membership_object = Membership.objects.get(name=user_object)"""
        membership_object = user_object.customer_membership.get()
        membership_deadline = membership_object.deadline
        membership_deadline = membership_deadline.replace(tzinfo=None)
        days_left = (membership_deadline - datetime.datetime.now(tz=None)).days
        if days_left < 10 and days_left >= 0 :
            context['membership_deadline_near'] = True
            context['days_left_expiry'] = days_left
        else :
            context['membership_deadline_near'] = False
    return render(request, 'Customer/displayCustomerNotification.html', context)


# Trainer Pages


@login_required
def DisplayTrainerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
    trainer_profile_object = user_object.trainer_profile_account.get()
    num_gym_class = len(trainer_profile_object.gym_class.all())
    return render(request, 'Trainer/profile.html', {'trainer' : trainer_profile_object, 'num_gym_class' : num_gym_class})


@login_required
def ChangeTrainerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
    trainer_profile_object = user_object.trainer_profile_account.get()
    if request.method == 'POST' :
        user_object.email = request.POST['email']
        trainer_profile_object.full_name = request.POST['full_name']
        trainer_profile_object.mobile = request.POST['mobile']
        trainer_profile_object.address = request.POST['address']
        trainer_profile_object.age = request.POST['age']
        trainer_profile_object.medical_history = request.POST['medical_history']
        trainer_profile_object.gender = request.POST['gender']
        user_object.save()
        trainer_profile_object.save()
        messages.success(request, 'Details entered have been updated.')
        return redirect('/trainer-profile')
    else :
        return render(request, 'Trainer/updateTrainer.html', {'trainer' : trainer_profile_object})



# Manager Pages


@login_required
def DisplayManagerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
    """manager_profile_object = ManagerProfile.objects.get(account=user_object)"""
    manager_profile_object = user_object.manager_profile_account.get()
    return render(request, 'Manager/profile.html', {'manager' : manager_profile_object})


@login_required
def ChangeManagerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
    manager_profile_object = user_object.manager_profile_account.get()
    if request.method == 'POST' :
        user_object.email = request.POST['email']
        manager_profile_object.full_name = request.POST['full_name']
        manager_profile_object.mobile = request.POST['mobile']
        manager_profile_object.address = request.POST['address']
        manager_profile_object.age = request.POST['age']
        manager_profile_object.gender = request.POST['gender']
        user_object.save()
        manager_profile_object.save()
        messages.success(request, 'Details entered have been updated.')
        return redirect('/manager-profile')
    else :
        return render(request, 'Manager/updateManager.html', {'manager' : manager_profile_object})


@login_required
def DisplayCustomerList(request) :
    customer_objects = CustomerProfile.objects.all()
    return render(request, 'Manager/displayCustomerList.html', {'customers' : customer_objects})


@login_required
def DisplayIndividualCustomer(request, cust_id) :
    customer_object = CustomerProfile.objects.get(id=cust_id)
    user_object = customer_object.account
    """membership_object = Membership.objects.get(name=customer_object.account)"""
    membership_object = user_object.customer_membership.get()
    membership_deadline = membership_object.deadline
    membership_deadline = membership_deadline.replace(tzinfo=None)
    if membership_deadline >= datetime.datetime.now(tz=None) :
        membership_status = "Active"
    else :
        membership_status = "Inactive"
    context = {'customer' : customer_object, 'membership_status' : membership_status, 'membership' : membership_object}
    return render(request, 'Manager/displayIndividualCustomer.html', context)


@login_required
def DisplayTrainerList(request) :
    trainer_objects = TrainerProfile.objects.all()
    return render(request, 'Manager/displayTrainerList.html', {'trainers' : trainer_objects})


@login_required
def DisplayIndividualTrainer(request, tra_id) :
    trainer_object = TrainerProfile.objects.get(id=tra_id)
    num_gym_class = len(trainer_object.gym_class.all())
    return render(request, 'Manager/displayIndividualTrainer.html', {'trainer' : trainer_object, 'num_gym_class' : num_gym_class})


@login_required
def DisplayManagerList(request) :
    manager_objects = ManagerProfile.objects.all()
    return render(request, 'Manager/displayManagerList.html', {'managers' : manager_objects})


@login_required
def DisplayIndividualManager(request, man_id) :
    # man_id is the id in the Manager Profile table
    manager_profile_object = ManagerProfile.objects.get(id=man_id)
    """print(man_id)
    print(request.user.manager_profile_account.all()[0].id)"""
    # If it is the currently logged in user
    if man_id == request.user.manager_profile_account.all()[0].id :
        return redirect('/manager-profile')
    # In all other cases
    return render(request, 'Manager/displayIndividualManager.html', {'manager' : manager_profile_object})


@login_required
def DisplayAdminList(request) :
    admin_user_objects = CustomUser.objects.filter(models.Q(is_superuser=True) | models.Q(role='A'))
    return render(request, 'Manager/displayAdminList.html', {'admin_users' : admin_user_objects})


@login_required
def DisplayIndividualAdmin(request, adm_id) :
    admin_user_object = CustomUser.objects.get(id=adm_id)
    return render(request, 'Manager/displayIndividualAdmin.html', {'admin_user' : admin_user_object})


# Pages common to Trainer and Manager


@login_required
def DisplayNotificationList(request) :
    # To delete the expired notifications from the database
    Notification.objects.filter(expiry__lt=datetime.datetime.now()).delete()
    # To display the active notifications
    if request.user.role == 'T' :
        notification_objects = Notification.objects.filter(author=request.user)
        num_notifications = len(notification_objects)
        base_template = 'Trainer/base.html'
    elif request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        notification_objects = Notification.objects.all()
        num_notifications = len(notification_objects)
        base_template = 'Manager/base.html'
    else :
        raise PermissionDenied()
        """return redirect('/')"""
    context = {'notifications' : notification_objects, 'num_notifications' : num_notifications, 'base_template' : base_template}
    return render(request, 'notification/displayNotificationList.html', context)


@login_required
def EditIndividualNotification(request, not_id) :
    notification_object = Notification.objects.get(id=not_id)
    if request.method == 'POST' :
        if request.user.role == 'T' and request.user != notification_object.author :
            raise PermissionDenied()
        elif request.user.role == 'T' or request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            notification_object.content = request.POST['content']
            # Format the recieved date time string into a datetime object that will be saved.
            expiry_date_time = datetime.datetime.strptime(request.POST['expiry'].replace('.', '') , '%B %d, %Y, %I:%M %p')
            notification_object.expiry = expiry_date_time.replace(tzinfo=None)
            gym_class_names = request.POST.getlist('gym_class')
            gym_classes = []
            for gym_class_itr in gym_class_names :
                gym_classes.append(GymClass.objects.get(name=gym_class_itr))
            notification_object.gym_class.set(gym_classes)
            notification_object.save()
            messages.success(request, 'Details entered have been updated.') 
            return redirect('/view-all-notifications')
        else :
            raise PermissionDenied()
    else :
        if request.user.role == 'T' and request.user != notification_object.author :
                raise PermissionDenied()
        elif request.user.role == 'T' :
            gym_classes = request.user.trainer_profile_account.get().gym_class.all()
            base_template = 'Trainer/base.html'
            return render(request, 'notification/editIndividualNotification.html', {'notification' : notification_object, 'gym_classes' : gym_classes, 'base_template' : base_template})
        elif request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            gym_classes = GymClass.objects.all()
            base_template = 'Manager/base.html'
            return render(request, 'notification/editIndividualNotification.html', {'notification' : notification_object, 'gym_classes' : gym_classes, 'base_template' : base_template})
        else :
            raise PermissionDenied()


@login_required
def PostNotification(request) :
    if request.method == 'POST' :
        notification_content = request.POST['content']
        notification_expiry = datetime.datetime.strptime(request.POST['expiry'].replace('.', '') , '%B %d, %Y, %I:%M %p')
        notification_expiry = notification_expiry.replace(tzinfo=None)
        gym_class_names = request.POST.getlist('gym_class')
        gym_classes = []
        for gym_class_itr in gym_class_names :
            gym_classes.append(GymClass.objects.get(name=gym_class_itr))
        notification_object = Notification.objects.create(author=request.user, content=notification_content, expiry=notification_expiry)
        notification_object.gym_class.set(gym_classes)
        notification_object.save()
        if notification_object.id :
            messages.success(request, 'A notification with the specfied details has been posted.') 
            return redirect('/view-all-notifications')
        else :
            messages.error(request, 'An Error occured while posting the notification.')
    else :
        if request.user.role == 'T' :
            gym_classes = request.user.trainer_profile_account.get().gym_class.all()
            base_template = 'Trainer/base.html'
        elif request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            gym_classes = GymClass.objects.all()
            base_template = 'Manager/base.html'
        else :
            raise PermissionDenied()
            return
        return render(request, 'notification/postNotification.html', {'gym_classes' : gym_classes, 'base_template' : base_template})


@login_required
def DeleteIndividualNotification(request, not_id) :
    notification_object = Notification.objects.get(id=not_id)
    if request.method == 'POST' :
        if request.user.role == 'T' and request.user != notification_object.author :
            raise PermissionDenied()
        elif request.user.role == 'T' or request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            notification_object.delete()
            messages.success(request, 'Details entered have been updated.') 
            return redirect('/view-all-notifications')
        else :
            raise PermissionDenied()
    else :
        if request.user.role == 'T' and request.user != notification_object.author :
                raise PermissionDenied()
        elif request.user.role == 'T' :
            base_template = 'Trainer/base.html'
            return render(request, 'notification/deleteNotification.html', {'notification' : notification_object, 'base_template' : base_template})
        elif request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            base_template = 'Manager/base.html'
            return render(request, 'notification/deleteNotification.html', {'notification' : notification_object, 'base_template' : base_template})
        else :
            raise PermissionDenied()