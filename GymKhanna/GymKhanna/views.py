from django.shortcuts import render
from django.http import HttpResponse

def Home_Page(request) :
    return render(request, 'home/home.html')

def Contact_Us(request) :
    return HttpResponse('Contact us')