from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url

urlpatterns = [
    path('', views.HomePage, name='home-page'),

    path('login/', auth_views.LoginView.as_view(), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), {'template_name': 'gymnasium/home.html'}, name='logout'),

    path('change-password/', views.changePassword, name='change-password'),

    path('aquatics/', views.Aquatics, name='aquatics'),

    path('view-announcements/', views.DisplayAnnouncements, name='view-announcements'),

    path('customer-profile/', views.DisplayCustomerProfile, name='customer-profile'),

    path('edit-customer-profile/', views.ChangeCustomerProfile, name='edit-customer-profile'),

    path('view-notifications/', views.DisplayNotification, name='display-notification'),

    path('manager-profile/', views.DisplayManagerProfile, name='manager-profile'),

    path('view-customer-list/', views.DisplayCustomerList, name='view-customer-list'),

]