from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url

urlpatterns = [
    path('', views.HomePage, name='home-page'),

    path('login/', auth_views.LoginView.as_view(), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), {'template_name': 'gymnasium/home.html'}, name='logout'),

    path('aquatics/', views.Aquatics, name='aquatics'),

    path('customer-profile/', views.DisplayCustomerProfile, name='customer-profile'),

]