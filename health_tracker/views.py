from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User #,MedWorkerRep
import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator
import time
# Create your views here.

# class NewUser(forms.ModelForm):
#     class Meta:
#         model=User
#         fields=['username','password','email']

def login_view(request):
    # if request.user.is_authenticated:
    #     return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        # code=request.POST['code']
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "health_tracker/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "health_tracker/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


