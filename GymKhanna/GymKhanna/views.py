from django.http import HttpResponse
from django.shortcuts import render

def Home_Page(request) :
    return render(request, 'home/home.html')

def Contact_Us(request) :
    return HttpResponse('Contact us')