from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render, redirect

from users.models import CustomUser, CustomerProfile, TrainerProfile, ManagerProfile
from users.forms import UserSignUpForm
from .models import Membership, Package, Notification, Equipment, Equipmenttype, Announcement, GymClass, AMC

import datetime


# ------------------------------------------------------- General Website Pages -------------------------------------------------------


def HomePage(request) :
    return render(request, 'gymnasium/home.html')


def FitnessClasses(request) :
    return render(request, 'gymnasium/fitnessClasses.html')


def Aquatics(request) :
    return render(request, 'gymnasium/aquatics.html')


def DisplayAnnouncements(request) :
    Announcement.objects.filter(expiry__lt=datetime.datetime.now()).delete()
    announcement_objects = Announcement.objects.all()
    num_announcements = len(announcement_objects)
    context = {'num_announcement' : num_announcements, 'announcements' : announcement_objects}
    return render(request, 'gymnasium/announcement.html', context)


@login_required
def changePassword(request) :
    # Choose the base template for different types of users.
    if request.user.role == 'C' :
        base_template = 'Customer/base.html'
        profile = '/customer-profile'
    elif request.user.role == 'T' :
        base_template = 'Trainer/base.html'
        profile = '/trainer-profile'
    else :
        base_template = 'Manager/base.html'
        profile = '/manager-profile'
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
        'base_template' : base_template,
        'profile' : profile
    })


def UserSignUp(request, role='C') :
    if role in ['T', 'M', 'A'] and request.user==None :
        raise forms.ValidationError('You do not have the authority to create User of this category.')
    elif role in ['C', 'T', 'M'] :
        if request.method == 'POST':
            form = UserSignUpForm(request.POST)
            if form.is_valid():
                userObjForm = form.cleaned_data
                username = userObjForm['username']
                email =  userObjForm['email']
                password =  userObjForm['password']
                if not (CustomUser.objects.filter(username=username).exists() or CustomUser.objects.filter(email=email).exists()):
                    user_object = CustomUser.objects.create_user(username, email, password)
                    user_object.role = role
                    user_object.save()
                    user = authenticate(username = username, password = password)
                    login(request, user)
                    if role == 'C' :
                        return redirect(CreateCustomerProfile)
                    elif role == 'T' :
                        return redirect(CreateTrainerProfile, user_id=user_object.id)  
                    elif role == 'M' :
                          return redirect(CreateManagerProfile, user_id=user_object.id)
                else:
                    raise forms.ValidationError('Looks like a username with that email or password already exists')
        else:
            form = UserSignUpForm()
        return render(request, 'registration/signup.html', {'form' : form})
    elif role == 'A' :
        raise forms.ValidationError('You do not have the authority to create a Admin Level User.')
    else :
        raise forms.ValidationError('Invalid Role. This system should not be intervened. Do not try this again !!!')


# ---------------------------------------------------------- Customer Pages -----------------------------------------------------------


@login_required
def CreateCustomerProfile(request) :
    if request.user.customer_profile_account.first() :
        return redirect(DisplayCustomerProfile)
    else :
        if request.method == 'POST' :
            user_object = CustomUser.objects.get(username=request.user.username)
            customer_profile_object = CustomerProfile.objects.create(
                account = request.user,
                full_name = request.POST['full_name'],
                reg_no = request.POST['reg_no'],
                mobile = request.POST['mobile'],
                address = request.POST['address'],
                age = request.POST['age'],
                weight = request.POST['weight'],
                medical_history = request.POST['medical_history'],
                allergies = request.POST['allergies'],
                gender = request.POST['gender']
            )
            # Recieve all the names of the selected options from the checkbox, get their objects and pass them to the set() method of the respective object.
            interested_equipments = request.POST.getlist('equipment')
            equipment_id_list = []
            for equipment_id in interested_equipments :
                equipment_id_list.append(Equipmenttype.objects.get(id=int(equipment_id)))
            customer_profile_object.equipment_interest.set(equipment_id_list)
            # Saving the modified objects
            user_object.save()
            customer_profile_object.save()
            messages.success(request, 'Details entered have been entered.')
            return redirect('/initial-gym-registration-choice')
        else :
            equipment_types = Equipmenttype.objects.all()
            return render(request, 'Customer/createCustomerProfile.html', {'equipment_types' : equipment_types})


@login_required
def DisplayCustomerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
    if user_object.customer_profile_account.first() :
        customer_profile_object = user_object.customer_profile_account.get()
        if not customer_profile_object.customer_membership.first() :
            membership_status = "Inactive"
            membership_object = None
        else :
            membership_object = customer_profile_object.customer_membership.get()
            membership_deadline = membership_object.deadline
            membership_deadline = membership_deadline.replace(tzinfo=None)
            if membership_deadline >= datetime.datetime.now(tz=None) :
                membership_status = "Active"
            else :
                membership_status = "Inactive"
        return render(request, 'Customer/profile.html', {'customer' : customer_profile_object, 'membership_status' : membership_status, 'membership' : membership_object})
    else :
        return redirect(CreateCustomerProfile)


@login_required
def ChangeCustomerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
    if user_object.customer_profile_account.first() :
        customer_profile_object = user_object.customer_profile_account.get()
        if request.method == 'POST' :
            user_object.email = request.POST['email']
            customer_profile_object.full_name = request.POST['full_name']
            customer_profile_object.reg_no = request.POST['reg_no']
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
            for equipment_id in interested_equipments :
                equipment_id_list.append(Equipmenttype.objects.get(id=int(equipment_id)))
            customer_profile_object.equipment_interest.set(equipment_id_list)
            # Saving the modified objects
            user_object.save()
            customer_profile_object.save()
            messages.success(request, 'Details entered have been updated.')
            return redirect('/customer-profile')
        else :
            equipment_types = Equipmenttype.objects.all()
            return render(request, 'Customer/updateCustomer.html', {'customer' : customer_profile_object, 'equipment_types' : equipment_types})
    else :
        return redirect(CreateCustomerProfile)


@login_required
def GymRegistrationChoice(request) :
    if request.user.role == 'C' :
        gym_packages = Package.objects.all()
        return render(request, 'Customer/gymRegistrationChoice.html', {'packages' : gym_packages})
    else :
        raise PermissionDenied()


@login_required
def MembershipRegistrationInstructions(request) :
    if request.user.role == 'C' :
        if request.method == 'POST' :
            request.session['readInstructions'] = True
            return redirect(MembershipRegistration)
        else :
            request.session['readInstructions'] = False
            return render(request, 'Customer/membershipRegistrationInstruction.html')
    else :
        raise PermissionDenied()


@login_required
def MembershipRegistration(request) :
    if request.user.role == 'C' :
        if ('readInstructions' in request.session) and (request.session['readInstructions'] == True) :
            if request.method == 'POST' :
                request.session['choosenPackageID'] = request.POST['package']
                return redirect(ConfirmOrderDetails)
            else :
                packages = Package.objects.all()
                return render(request, 'Customer/membershipRegistration.html', {'packages' : packages})
        else :
            return redirect(MembershipRegistrationInstructions)
    else :
        raise PermissionDenied()


@login_required
def ConfirmOrderDetails(request) :
    if request.user.role == 'C' :
        if ('readInstructions' in request.session) and (request.session['readInstructions'] == True) :
            if ('choosenPackageID' in request.session) and (request.session['choosenPackageID'] != None) :
                user_object = request.user
                if request.method == 'POST' :
                    """--------------------------------------------------------------------------------------------------------------------------------"""
                    # Needs work to be done here whe implementing payment portal
                    PaymentPortal
                    return HttpResponse('Payment Portal')
                else :
                    package_object = Package.objects.get(id=int(request.session['choosenPackageID']))
                    if user_object.customer_profile_account.first() :
                        customer_profile_object = user_object.customer_profile_account.get()
                        if customer_profile_object.customer_membership.first() :
                            membership_object = customer_profile_object.customer_membership.get()
                            present_deadline = membership_object.deadline.replace(tzinfo=None)
                        else :
                            present_deadline = datetime.datetime.now(tz=None)
                        future_deadline = present_deadline + datetime.timedelta(int(package_object.duration)*30)
                        context = {'future_deadline': future_deadline, 'package' : package_object, 'customer' : customer_profile_object}
                        return render(request, 'Customer/confirmOrderDetails.html', context)
                    else :
                        redirect(CreateCustomerProfile)
            else :
                return redirect(MembershipRegistration)
        else :
            return redirect(MembershipRegistrationInstructions)
    else :
        raise PermissionDenied()


@login_required
def DisplayCustomerNotification(request) :
    # To delete the expired notifications from the database
    Notification.objects.filter(expiry__lt=datetime.datetime.now()).delete()
    # To display the active notifications
    user_object = CustomUser.objects.get(username=request.user)
    if user_object.customer_profile_account.first() :
        customer_profile_object = CustomerProfile.objects.get(account=user_object)
        gym_class_object = customer_profile_object.gym_class
        notification_objects = Notification.objects.filter(gym_class=gym_class_object)
        num_notifications = len(notification_objects)
        context = {'num_notifications' : num_notifications, 'notifications' : notification_objects}
        if user_object.role == 'C' :
            if customer_profile_object.customer_membership.first() :
                membership_object = customer_profile_object.customer_membership.get()
                membership_deadline = membership_object.deadline
                membership_deadline = membership_deadline.replace(tzinfo=None)
                days_left = (membership_deadline - datetime.datetime.now(tz=None)).days
                if days_left < 10 and days_left >= 0 :
                    context['membership_deadline_near'] = True
                    context['days_left_expiry'] = days_left
                else :
                    context['membership_deadline_near'] = False
        return render(request, 'Customer/displayCustomerNotification.html', context)
    else :
        return redirect(CreateCustomerProfile)


# ----------------------------------------------------------- Trainer Pages ------------------------------------------------------------


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


@login_required
def DisplayTrainerGymClassList(request) :
    if request.user.role == 'T' :
        trainer_profile_object = request.user.trainer_profile_account.get()
        gym_class_objects = trainer_profile_object.gym_class.all()
        num_gym_classes = len(gym_class_objects)
        return render(request, 'Trainer/displayTrainerGymClassList.html', {'trainer' : trainer_profile_object, 'gym_classes' : gym_class_objects, 'num_gym_classes' : num_gym_classes})
    else :
        raise PermissionDenied()


@login_required
def DisplayTrainerIndividualGymClass(request, cls_id) :
    if request.user.role == 'T' :
        current_trainer_profile_object = request.user.trainer_profile_account.get()
        possible_gym_class_objects = current_trainer_profile_object.gym_class.all()
        gym_class_object = GymClass.objects.get(id=cls_id)
        if gym_class_object in possible_gym_class_objects :
            customer_profile_objects = gym_class_object.customer_profile_for_gym_class.all()
            num_customers = len(customer_profile_objects)
            trainer_profile_objects = gym_class_object.allocated_trainers.all()
            num_trainers = len(trainer_profile_objects)
            context = {
                'gym_class' : gym_class_object,
                'customers' : customer_profile_objects,
                'num_customers' : num_customers,
                'trainers' : trainer_profile_objects,
                'num_trainers' : num_trainers,
                'current_trainer' : current_trainer_profile_object,
            }
            return render(request, 'Trainer/displayTrainerIndividualGymClass.html', context)
        else :
            raise PermissionDenied()
    else :
        raise PermissionDenied()


# ----------------------------------------------------------- Manager Pages ------------------------------------------------------------


@login_required
def DisplayManagerProfile(request) :
    user_object = CustomUser.objects.get(username=request.user)
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
    membership_object = customer_object.customer_membership.get()
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


@login_required
def DisplayAnnouncementList(request) :
    # To delete the expired Announcements from the database
    Announcement.objects.filter(expiry__lt=datetime.datetime.now()).delete()
    # To display the active Announcements
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        announcement_objects = Announcement.objects.all()
        num_announcements = len(announcement_objects)
    else :
        raise PermissionDenied()
    context = {'announcements' : announcement_objects, 'num_announcements' : num_announcements}
    return render(request, 'Manager/displayAnnouncementList.html', context)


@login_required
def EditIndividualAnnouncement(request, ann_id) :
    announcement_object = Announcement.objects.get(id=ann_id)
    if request.method == 'POST' :
        if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            announcement_object.content = request.POST['content']
            # Format the recieved date time string into a datetime object that will be saved.
            expiry_date_time = datetime.datetime.strptime(request.POST['expiry'].replace('.', '') , '%B %d, %Y, %I:%M %p')
            announcement_object.expiry = expiry_date_time.replace(tzinfo=None)
            announcement_object.save()
            messages.success(request, 'Details entered have been updated.') 
            return redirect('/view-all-announcements')
        else :
            raise PermissionDenied()
    else :
        if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            return render(request, 'Manager/editIndividualAnnouncement.html', {'announcement' : announcement_object})
        else :
            raise PermissionDenied()


@login_required
def PostAnnouncement(request) :
    if request.method == 'POST' :
        if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            announcement_content = request.POST['content']
            announcement_expiry = datetime.datetime.strptime(request.POST['expiry'].replace('.', '') , '%B %d, %Y, %I:%M %p')
            announcement_expiry = announcement_expiry.replace(tzinfo=None)
            announcement_object = Announcement.objects.create(author=request.user, content=announcement_content, expiry=announcement_expiry)
            if announcement_object.id :
                messages.success(request, 'A new Announcement with the specfied details has been posted.') 
                return redirect('/view-all-announcements')
            else :
                messages.error(request, 'An Error occured while posting the Announcement.')
        else :
            raise PermissionDenied()
    else :
        if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            return render(request, 'Manager/postAnnouncement.html')
        else :
            raise PermissionDenied()


@login_required
def DeleteIndividualAnnouncement(request, ann_id) :
    announcement_object = Announcement.objects.get(id=ann_id)
    if request.method == 'POST' :
        if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            announcement_object.delete()
            messages.success(request, 'Details entered have been updated.') 
            return redirect('/view-all-announcements')
        else :
            raise PermissionDenied()
    else :
        if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            return render(request, 'Manager/deleteAnnouncement.html', {'announcement' : announcement_object})
        else :
            raise PermissionDenied()


@login_required
def CreateEquipmentType(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        if request.method == 'POST' :
            eq_name = request.POST['name']
            eq_description = request.POST['description']
            equipment_type_object = Equipmenttype.objects.create(name=eq_name, description=eq_description)
            if equipment_type_object.id :
                messages.success(request, 'A Equipment type has been created successfully.')
                return redirect('/view-all-equipment-types')
            else :
                messages.error(request, 'An Error occured while creating the Equipment type.')
        else :
            return render(request, 'Manager/createEquipmentType.html')
    else :
        raise PermissionDenied()


@login_required
def DisplayEquipmentTypeList(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        equipment_type_objects = Equipmenttype.objects.all()
        num_equipment_type = len(equipment_type_objects)
        context = {'equipment_types' : equipment_type_objects, 'num_equipment_type' : num_equipment_type}
        return render(request, 'Manager/displayEquipmentTypeList.html', context)
    else :
        raise PermissionDenied()


@login_required
def EditEquipmentType(request, eqty_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        equipment_type_object = Equipmenttype.objects.get(id=eqty_id)
        if request.method == 'POST' :
            equipment_type_object.name = request.POST['name']
            equipment_type_object.description = request.POST['description']
            equipment_type_object.save()
            messages.success(request, 'The Equipment type has been modified successfully.')
            return redirect( '/view-all-equipment-types')
        else :
            return render(request, 'Manager/editEquipmentType.html', {'equipment_type' : equipment_type_object})
    else :
        raise PermissionDenied()


@login_required
def DeleteEquipmentType(request, eqty_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        equipment_type_object = Equipmenttype.objects.get(id=eqty_id)
        if request.method == 'POST' :
            equipment_type_object.delete()
            messages.success(request, 'The Equipment type has been deleted successfully.')
            return redirect('/view-all-equipment-types')
        else :
            equipment_objects = equipment_type_object.equipments.all()
            num_equipments = len(equipment_objects)
            context = {'equipment_type' : equipment_type_object, 'equipments' : equipment_objects, 'num_equipments' : num_equipments}
            return render(request, 'Manager/deleteEquipmentType.html', context)
    else :
        raise PermissionDenied()


@login_required
def CreateEquipment(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        if request.method == 'POST' :
            eq_name = request.POST['name']
            eq_detail = request.POST['detail']
            eq_purchase = request.POST['purchase']
            eq_type_id = request.POST['eq_type']
            eq_type_object = Equipmenttype.objects.get(id=int(eq_type_id))
            equipment_object = Equipment.objects.create(name=eq_name, detail=eq_detail, date_of_purchase=eq_purchase, equipment_type=eq_type_object)
            if equipment_object.id :
                messages.success(request, 'The Equipment record has been created successfully.')
                return redirect('/view-all-equipment')
            else :
                messages.error(request, 'An Error occured while creating the Equipment record.')
        else :
            equipment_type_objects = Equipmenttype.objects.all()
            return render(request, 'Manager/createEquipment.html', {'equipment_types' : equipment_type_objects})
    else :
        raise PermissionDenied()


@login_required
def DisplayAllEquipmentList(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        equipment_objects = Equipment.objects.all()
        num_equipment = len(equipment_objects)
        context = {'equipments' : equipment_objects, 'num_equipment' : num_equipment}
        return render(request, 'Manager/displayAllEquipmentList.html', context)
    else :
        raise PermissionDenied()


@login_required
def EditEquipment(request, eq_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        equipment_object = Equipment.objects.get(id=eq_id)
        if request.method == 'POST' :
            equipment_object.name = request.POST['name']
            equipment_object.detail = request.POST['detail']
            equipment_object.date_of_purchase = request.POST['purchase']
            eq_type_id = request.POST['eq_type']
            equipment_object.equipment_type = Equipmenttype.objects.get(id=int(eq_type_id))
            equipment_object.save()
            messages.success(request, 'The Equipment record has been modified successfully.')
            return redirect('/view-all-equipment')
        else :
            equipment_type_objects = Equipmenttype.objects.all()
            return render(request, 'Manager/editEquipment.html', {'equipment' : equipment_object, 'equipment_types' : equipment_type_objects})
    else :
        raise PermissionDenied()


@login_required
def DeleteEquipment(request, eq_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        equipment_object = Equipment.objects.get(id=eq_id)
        if request.method == 'POST' :
            equipment_object.delete()
            messages.success(request, 'The Equipment record has been deleted successfully.')
            return redirect('/view-all-equipment')
        else :
            context = {'equipment' : equipment_object}
            return render(request, 'Manager/deleteEquipment.html', context)
    else :
        raise PermissionDenied()


@login_required
def DisplayEquipmentListOfType(request, eqty_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        equipment_type_object = Equipmenttype.objects.get(id=eqty_id)
        equipment_objects = Equipment.objects.filter(equipment_type=equipment_type_object)
        num_equipment = len(equipment_objects)
        context = {'equipments' : equipment_objects, 'num_equipment' : num_equipment, 'equipment_type' : equipment_type_object}
        return render(request, 'Manager/displayEquipmentListOfType.html', context)
    else :
        raise PermissionDenied()


@login_required
def AddAMC(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        if request.method == 'POST' :
            eq_id = request.POST['equipment']
            equipment_object = Equipment.objects.get(id=int(eq_id))
            start = request.POST['start_date']
            renew = request.POST['renewal_date']
            present_price = request.POST['price']
            amc_object = AMC.objects.create(equipment=equipment_object, start_date=start, renewal_date=renew, count=1, price=present_price)
            if amc_object.id :
                messages.success(request, 'The AMC record for the equipment has been created successfully.')
                return redirect('/view-all-amc')
            else :
                messages.error(request, 'An Error occured while adding the AMC for the Equipment.')
        else :
            equipment_object_list = Equipment.objects.filter(amc=None)
            context = {'equipments' : equipment_object_list}
            return render(request, 'Manager/addAMC.html', context)
    else :
        raise PermissionDenied()


@login_required
def ModifyAMC(request, amc_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        amc_object = AMC.objects.get(id=amc_id)
        if request.method == 'POST' :
            amc_object.start_date = request.POST['start_date']
            amc_object.renewal_date = request.POST['renewal_date']
            amc_object.price = request.POST['price']
            amc_object.count = request.POST['count']
            amc_object.save()
            messages.success(request, 'The AMC record for the equipment has been modified successfully.')
            return redirect('/view-all-amc')
        else :
            new_date = datetime.date.today()
            if amc_object.renewal_date >= datetime.date.today() :
                status = False
            else :
                status = True
            return render(request, 'Manager/modifyAMC.html', {'amc' : amc_object, 'new_date' : new_date, 'status' : status})
    else :
        raise PermissionDenied()


@login_required
def DisplayAMCList(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        amc_objects = AMC.objects.all()
        num_amcs = len(amc_objects)
        return render(request, 'Manager/displayAMCList.html', {'amcs' : amc_objects, 'num_amcs' : num_amcs})
    else :
        raise PermissionDenied()


@login_required
def DeleteAMC(request, amc_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        amc_object = AMC.objects.get(id=amc_id)
        if request.method == 'POST' :
            amc_object.delete()
            messages.success(request, 'The AMC record has been deleted successfully.')
            return redirect('/view-all-amc')
        else :
            return render(request, 'Manager/deleteAMC.html', {'amc' : amc_object})
    else :
        raise PermissionDenied()


@login_required
def CreateGymPackage(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        if request.method == 'POST' :
            pkg_name = request.POST['name']
            pkg_price = request.POST['price']
            pkg_duration = request.POST['duration']
            package_object = Package.objects.create(name=pkg_name, price=pkg_price, duration=pkg_duration)
            if package_object.id :
                messages.success(request, 'A new Package record has been created.')
                return redirect('/view-all-gym-package') 
            else :
                messages.error(request, 'An Error occured while creating the record.')
        else :
            return render(request, 'Manager/createGymPackage.html')
    else :
        raise PermissionDenied()

@login_required
def DisplayGymPackageList(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        gym_package_objects = Package.objects.all()
        num_gym_packages = len(gym_package_objects)
        return render(request, 'Manager/displayGymPackageList.html', {'packages' : gym_package_objects, 'num_packages' : num_gym_packages})
    else :
        raise PermissionDenied()


@login_required
def DisplayIndividualGymPackage(request, pkg_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        gym_package_object = Package.objects.get(id=pkg_id)
        customer_profile_objects = gym_package_object.customer_profile_for_package.all()
        num_customers = len(customer_profile_objects)
        context = {
            'package' : gym_package_object,
            'customers' : customer_profile_objects,
            'num_customers' : num_customers,
        }
        return render(request, 'Manager/displayIndividualGymPackage.html', context)
    else :
        raise PermissionDenied()


@login_required
def EditGymPackage(request, pkg_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        gym_package_object = Package.objects.get(id=pkg_id)
        if request.method == 'POST' :
            gym_package_object.name = request.POST['name']
            gym_package_object.price = request.POST['price']
            gym_package_object.duration = request.POST['duration']
            gym_package_object.save()
            messages.success(request, 'The Gym Package record has been modified successfully.')
            return redirect('/view-all-gym-package')
        else :
            customer_profile_objects = gym_package_object.customer_profile_for_package.all()
            num_customers = len(customer_profile_objects)
            return render(request, 'Manager/editGymPackage.html', {'package' : gym_package_object, 'num_customers' : num_customers})
    else :
        raise PermissionDenied()


@login_required
def DeleteGymPackage(request, pkg_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        gym_package_object = Package.objects.get(id=pkg_id)
        customer_profile_objects = gym_package_object.customer_profile_for_package.all()
        if len(customer_profile_objects) > 0 :
            messages.error(request, 'There are some customers associated with this Gym Package. Contact the administrator for further assistence in this matter.')
            raise PermissionDenied()
        else :
            if request.method == 'POST' :
                gym_package_object.delete()
                messages.success(request, 'The Gym Package record has been deleted.')
                return redirect('/view-all-gym-package')
            else :
                return render(request, 'Manager/deleteGymPackage.html', {'package' : gym_package_object})
    else :
        raise PermissionDenied()


@login_required
def CreateGymClass(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        if request.method == 'POST' :
            class_name = request.POST['name']
            class_timings = request.POST['timings']
            gym_class_object = GymClass.objects.create(name=class_name, timings=class_timings)
            if gym_class_object.id :
                messages.success(request, 'A new Gym Class record has been created.')
                return redirect('/view-all-gym-class') 
            else :
                messages.error(request, 'An Error occured while creating the record.')
        else :
            return render(request, 'Manager/createGymClass.html')
    else :
        raise PermissionDenied()


@login_required
def DisplayGymClassList(request) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        gym_class_objects = GymClass.objects.all()
        num_gym_classes = len(gym_class_objects)
        return render(request, 'Manager/displayGymClassList.html', {'gym_classes' : gym_class_objects, 'num_gym_classes' : num_gym_classes})
    else :
        raise PermissionDenied()


@login_required
def DisplayIndividualGymClass(request, cls_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        gym_class_object = GymClass.objects.get(id=cls_id)
        customer_profile_objects = gym_class_object.customer_profile_for_gym_class.all()
        num_customers = len(customer_profile_objects)
        trainer_profile_objects = gym_class_object.allocated_trainers.all()
        num_trainers = len(trainer_profile_objects)
        context = {
            'gym_class' : gym_class_object,
            'customers' : customer_profile_objects,
            'num_customers' : num_customers,
            'trainers' : trainer_profile_objects,
            'num_trainers' : num_trainers,
        }
        return render(request, 'Manager/displayIndividualGymClass.html', context)
    else :
        raise PermissionDenied()


@login_required
def EditGymClass(request, cls_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        gym_class_object = GymClass.objects.get(id=cls_id)
        if request.method == 'POST' :
            gym_class_object.name = request.POST['name']
            gym_class_object.timings = request.POST['timings']
            gym_class_object.save()
            messages.success(request, 'The Gym Class record has been modified successfully.')
            return redirect('/view-all-gym-class')
        else :
            return render(request, 'Manager/editGymClass.html', {'gym_class' : gym_class_object})
    else :
        raise PermissionDenied()


@login_required
def DeleteGymClass(request, cls_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        gym_class_object = GymClass.objects.get(id=cls_id)
        customer_profile_objects = gym_class_object.customer_profile_for_gym_class.all()
        trainer_profile_objects = gym_class_object.allocated_trainers.all()
        if request.method == 'POST' :
            # All the customers who have been registered under this class should be cleared from this class.
            for cust in customer_profile_objects :
                cust.gym_class = None
                cust.save()
            # All the trainers who take care of this class should not have this class under them.
            for trainer in trainer_profile_objects :
                trainer_gym_classes = list(trainer.gym_class.all())
                if gym_class_object in trainer_gym_classes :
                    trainer_gym_classes.remove(gym_class_object)
                trainer.gym_class.set(trainer_gym_classes)
                trainer.save()
            gym_class_object.delete()
            messages.success(request, 'The Gym Class record has been deleted.')
            if len(customer_profile_objects) > 0 :
                # There are a few customers now who have not been allocated any new gym class.
                return redirect(AllocateCustomerGymClass, customers=customer_profile_objects )
            else :
                # There are no customers who have not been alloted any class.
                return redirect('/view-all-gym-class')
        else :
            num_customers = len(customer_profile_objects)
            num_trainers = len(trainer_profile_objects)
            context = {
                'gym_class' : gym_class_object,
                'customers' : customer_profile_objects,
                'num_customers' : num_customers,
                'trainers' : trainer_profile_objects,
                'num_trainers' : num_trainers,
            }
            return render(request, 'Manager/deleteGymClass.html', context)
    else :
        raise PermissionDenied()


@login_required
def AllocateCustomerGymClass(request, customers=None) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        if customers != None :
            customer_profile_objects = customers
        else :
            customer_profile_objects = CustomerProfile.objects.filter(gym_class=None)
        if request.method == 'POST' :
            for customer in customer_profile_objects :
                gym_class_id = request.POST[str(customer.id)]
                if gym_class_id != 'None' :
                    customer.gym_class = GymClass.objects.get(id=int(gym_class_id))
                    customer.save()
            return redirect('/view-customer-list')
        else :
            num_customer_profiles = len(customer_profile_objects)
            gym_classes = GymClass.objects.all()
            return render(request, 'Manager/allocateCustomerGymClass.html', {'customers' : customer_profile_objects, 'num_customers' : num_customer_profiles, 'gym_classes' : gym_classes})
    else :
        raise PermissionDenied()


@login_required
def ModifyCustomerGymClass(request, cust_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        customer_profile_object = CustomerProfile.objects.get(id=cust_id)
        if request.method == 'POST' :
            gym_class_id = request.POST['gym_class']
            customer_profile_object.gym_class = GymClass.objects.get(id=int(gym_class_id))
            customer_profile_object.save()
            messages.success(request, 'The Gym Class record has been allocated for the customer.')
            return redirect('/view-customer-list')
        else :
            gym_classes = GymClass.objects.all()
            return render(request, 'Manager/modifyCustomerGymClass.html', {'customer' : customer_profile_object, 'gym_classes' : gym_classes})
    else :
        raise PermissionDenied()


@login_required
def ModifyTrainerGymClass(request, tra_id) :
    if request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
        trainer_profile_object = TrainerProfile.objects.get(id=tra_id)
        if request.method == 'POST' :
            gym_class_ids = request.POST.getlist('gym_class')
            gym_classes = []
            for gym_class_itr in gym_class_ids :
                gym_classes.append(GymClass.objects.get(id=int(gym_class_itr)))
            trainer_profile_object.gym_class.set(gym_classes)
            trainer_profile_object.save()
            messages.success(request, 'The Trainer has been allocated to the selected gym classes.')
            return redirect('/view-trainer-list')
        else :
            gym_classes = GymClass.objects.all()
            return render(request, 'Manager/modifyTrainerGymClass.html', {'trainer' : trainer_profile_object, 'gym_classes' : gym_classes})
    else :
        raise PermissionDenied()


# ------------------------------------------------- Pages common to Trainer and Manager -------------------------------------------------


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
            gym_class_ids = request.POST.getlist('gym_class')
            gym_classes = []
            for gym_class_itr in gym_class_ids :
                gym_classes.append(GymClass.objects.get(id=int(gym_class_itr)))
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
        if request.user.role == 'T' or request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            notification_content = request.POST['content']
            notification_expiry = datetime.datetime.strptime(request.POST['expiry'].replace('.', '') , '%B %d, %Y, %I:%M %p')
            notification_expiry = notification_expiry.replace(tzinfo=None)
            gym_class_ids = request.POST.getlist('gym_class')
            gym_classes = []
            for gym_class_itr in gym_class_ids :
                gym_classes.append(GymClass.objects.get(id=int(gym_class_itr)))
            notification_object = Notification.objects.create(author=request.user, content=notification_content, expiry=notification_expiry)
            notification_object.gym_class.set(gym_classes)
            notification_object.save()
            if notification_object.id :
                messages.success(request, 'A new notification with the specfied details has been posted.') 
                return redirect('/view-all-notifications')
            else :
                messages.error(request, 'An Error occured while posting the notification.')
        else :
            raise PermissionDenied()
    else :
        if request.user.role == 'T' :
            gym_classes = request.user.trainer_profile_account.get().gym_class.all()
            base_template = 'Trainer/base.html'
        elif request.user.role == 'M' or request.user.role == 'A' or request.user.is_superuser :
            gym_classes = GymClass.objects.all()
            base_template = 'Manager/base.html'
        else :
            raise PermissionDenied()
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