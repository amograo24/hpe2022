from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, MedWorkerRep, Patients 
import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator
import time
from .utils import gen_unique_id
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

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        code=request.POST["code"]

        if code not in ['NoU','HCW-I-SP-MSh']:
            return render(request, "health_tracker/register.html", {
                "message": "An error occured, please fill the form again."
            })
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            if code.lower()=="nou":
                aadharid=request.POST['aadharid']
                gen_unique_id(aadharid, request.user)
                # wbid=(gen_unique_id(12, 16))
                # person=request.user
                # patient=Patients(aadharid=aadharid,wbid=wbid,person=person)
                # patient.save()
            elif code.lower()=='hcw-i-sp-msh':
                reg_no=request.POST['reg_no']
                hcwvid=(gen_unique_id(12, 16)) # kushal gotta make one here
                account=request.user
                department=request.POST['department']
                medworkerrep=MedWorkerRep(reg_no=reg_no,hcwvid=hcwvid,account=account,department=department)
                medworkerrep.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def test(request):
    return HttpResponse("200 OK")