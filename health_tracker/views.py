from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, MedWorkerRep, Patients
from django.contrib.admin.widgets import AdminDateWidget
import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator
import time
from .utils import gen_unique_id, get_hcw_vid, return_qr_code
from django.core.validators import MinLengthValidator
# Create your views here.

# class Register(forms.ModelForm):
#     class Meta:
#         model=User
#         fields=[]

class RegisterForm(forms.Form):
    division = forms.ChoiceField(label="Choose any of the following that apply to you", choices=[
        ('D/HCW/MS', 'Doctor/Health Care Worker/Medical Staff'),
        ('I/SP', 'Insurance/Health Service Provider'),
        ('MSh', 'Medical Shop'),
        ('NoU','None of the Above')
        ], required=True)
    full_name = forms.CharField(label='Full Name', max_length=200, required=True)
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=True)
    reg_no = forms.CharField(max_length=20, label='Registration no.', required=True)
    aadharid = forms.CharField(max_length=12, label='Aadhar ID', required=True, widget=forms.TextInput(attrs={"type":"number"}),validators=[MinLengthValidator(12)])
    department = forms.CharField(max_length=100, required=False)

class LoginForm(forms.Form):
    username=forms.CharField(label="WB ID/HCWV ID",max_length=16, validators=[MinLengthValidator(11)])
    password=forms.CharField(label='Password', widget=forms.PasswordInput, required=True)


def index(request):
    return render(request,"health_tracker/index.html")

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method=="POST":
        form=LoginForm(request.POST)
        if form.is_valid():
            # Attempt to sign user in
            username=form.cleaned_data["username"]
            password=form.cleaned_data["password"]
            # code=request.POST['code']
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "health_tracker/login.html", {
                    "form":form,
                    "message": "Invalid username and/or password."
                })
        else:
            return render(request,"health_tracker/login.html", {
                "form":form
            })
    else:
        return render(request, "health_tracker/login.html",{
            "form":LoginForm()
        })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    # verify aadhar number is inputted, etc
    if request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            # username=form.cleaned_data['username']
            full_name=form.cleaned_data['full_name']
            # first_name=form.cleaned_data['first_name']
            # last_name=form.cleaned_data['last_name']
            email=form.cleaned_data['email']
            # dob=form.cleaned_data['dob']
            password=form.cleaned_data['password']
            confirm_password=form.cleaned_data['confirm_password']
            division=form.cleaned_data['division']

            if password != confirm_password:
                return render(request, "health_tracker/register.html", {
                    "form":form,
                    "message": "Passwords must match."
            })
            try:
               # Creating the user here
                if division.lower()=="nou" or division.lower()==None:
                    user = gen_unique_id(email=email, password=password)
                    aadharid=form.cleaned_data['aadharid']
                    if len(aadharid)!=12 or aadharid.isnumeric()==False:
                        return render(request, "health_tracker/register.html",{
                            "form":form,
                            "message":"Your Aadhar ID must have only 12 digits!"
                        })
                    # what if aadhar id already exisits?
                    if Patients.objects.filter(aadharid=aadharid): #is this correct?
                        return render(request, "health_tracker/register.html",{
                            "form":form,
                            "message":"An account with this Aadhar ID already exists!"
                        })
                    print(request.user.pk, request.user, request.user.username)
                    Patients(aadharid=aadharid, full_name=full_name, wbid=user.username, person=user).save()

                elif division.lower() in ['d/hcw/ms','i/sp','msh']:
                    user = get_hcw_vid(email=email, password=password)
                    reg_no=form.cleaned_data['reg_no']
                    dept=form.cleaned_data['department']
                    MedWorkerRep(reg_no=reg_no,department=dept,full_com_name=full_name, hcwvid=user.username, account=user).save()

            except IntegrityError:
                return render(request, "health_tracker/register.html", {
                    "form":form,
                    "message": "Username already taken."
            })
            login(request, user)
            return HttpResponseRedirect(reverse("index")) #redirect to my page
        else:
            return render(request, "health_tracker/register.html",{
                "form":form
            })
    return render(request, "health_tracker/register.html",{
        "form":RegisterForm()
    })


def myprofile(request):
    if request.user.is_authenticated:
        user_type=request.user
        if Patients.objects.filter(wbid=request.user):
            user=Patients.objects.get(wbid=request.user)
        elif MedWorkerRep.objects.filter(hcwvid=request.user):
            user=MedWorkerRep.objects.get(hcwbid=request.user)
        print(user_type.division)
        print(user)
        # print(user.division)
        return render(request,"health_tracker/myprofile.html",{
            "image":return_qr_code(request.user),
            "user":user,
            "user_type":user_type,
            "non_patient":['d/hcw/ms','i/sp','msh']
        })
    else:
        return HttpResponseRedirect(reverse("login"))

# def other_profile(request,id):
    # if request.user.is_authenticated:
    #     if request.user==id:
    #       return HttpResponseRedirect(reverse("myprofile"))
    #     if Patients.objects.filter(wbid=id):
    #         pass
    #     elif MedWorkerRep.objects.filter(hcwvid=id):
    #         pass
    #     else:
    #         raise Http404(f"'{category_name}' category does not exist!") 
    # else:
    #     return HttpResponseRedirect(reverse("login"))



# def register(request):
#     if request.method == "POST":
#         username = request.POST["username"]
#         email = request.POST["email"]
#         division=request.POST["division"]

#         if division not in ['NoU','D/HCW/MS','I/SP','MSh']:
#             return render(request, "health_tracker/register.html", {
#                 "message": "An error occured, please fill the form again."
#             })
#         # Ensure password matches confirmation
#         password = request.POST["password"]
#         confirmation = request.POST["confirmation"]
#         if password != confirmation:
#             return render(request, "health_tracker/register.html", {
#                 "message": "Passwords must match."
#             })

#         # Attempt to create new user
#         try:
#             user = User.objects.create_user(username, email, password,)
#             user.save()
#             if division.lower()=="nou" or division.lower()==None:
#                 aadharid=request.POST['aadharid']
#                 gen_unique_id(aadharid, request.user)
#                 # wbid=(gen_unique_id(12, 16))
#                 # person=request.user
#                 # patient=Patients(aadharid=aadharid,wbid=wbid,person=person)
#                 # patient.save()
#             elif division.lower() in ['d/hcw/ms','i/sp','msh']:
#                 reg_no=request.POST['reg_no']
#                 hcwvid=(gen_unique_id(12, 16)) # kushal gotta make one here
#                 account=request.user
#                 department=request.POST['department']
#                 medworkerrep=MedWorkerRep(reg_no=reg_no,hcwvid=hcwvid,account=account,department=department)
#                 medworkerrep.save()
#         except IntegrityError:
#             return render(request, "health_tracker/register.html", {
#                 "form":form,
#                 "message": "Username already taken."
#             })
#         login(request, user)
#         return HttpResponseRedirect(reverse("index"))
#     else:
#         return render(request, "health_tracker/register.html",{
#             "form":form
#         })


def test(request):
    return HttpResponse("200 OK")