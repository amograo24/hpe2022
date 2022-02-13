from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, MedWorkerRep, Patients, Notification
from django.contrib.admin.widgets import AdminDateWidget
import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator
import time
from .utils import gen_unique_id, get_hcw_vid, return_qr_code
from django.core.validators import MinLengthValidator
from django.core.files.storage import FileSystemStorage,default_storage
# Create your views here.


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

class UploadDoc(forms.Form):
    document=forms.FileField(label="Select a file",help_text="Upload")

def upload_file(request):
    if request.method == "POST":
        form=UploadDoc(request.POST,request.FILES)
        print("Outside",request.FILES)
        if form.is_valid():
            pass
    return render(request, "health_tracker/file_upload.html",{
        "form":UploadDoc()
    })

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
                    user = get_hcw_vid(email=email, password=password, division=division)
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



def index(request):
    if request.user.is_authenticated:
        user=User.objects.get(username=request.user)
        user_type=user.division.lower()
        image=None
        if user_type=='nou':
            user=Patients.objects.get(person=user)
            image=return_qr_code(request.user)
        elif user_type in ['d/hcw/ms','i/sp','msh']:
            user=MedWorkerRep.objects.get(account=user)   

        return render(request,"health_tracker/myprofile.html",{
            "image":image,
            "user":user,
            "nou":user_type=='nou',
            "non_nou":user_type in ['d/hcw/ms','i/sp','msh']
        })
    else:
        return render(request,"health_tracker/index.html")

def other_profile(request,id):
    if request.user.is_authenticated:
        if request.user==id:
            return HttpResponseRedirect(reverse("index"))
        viewer=User.objects.get(username=request.user)
        viewer_type=viewer.division.lower()
        try:
            profile=User.objects.get(username=id)
            profile_type=profile.division.lower()
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse("index"))
        if viewer_type==profile_type: # make it more secure
            return HttpResponseRedirect(reverse("index"))
        if viewer_type in ['d/hcw/ms','i/sp','msh'] and profile_type in ['d/hcw/ms','i/sp','msh']:
            return HttpResponseRedirect(reverse("index"))
        if profile_type=='nou':
            profile=Patients.objects.get(person=profile)
            viewer=MedWorkerRep.objects.get(account=viewer)
            if viewer in profile.hcw_v.all():
                if viewer_type=='d/hcw/ms':
                    # show all documents of profile
                    pass
                elif viewer_type=='i/sp':
                    # show all documents of profile uploaded by this i/sp
                    pass
                elif viewer_type=='msh':
                    # show all documents of profile uploaded by this msh
                    pass
            else:
                return HttpResponseRedirect(reverse("index"))
        elif profile_type in ['d/hcw/ms','i/sp','msh']:
            profile=MedWorkerRep.objects.get(account=profile)
            viewer=Patients.object.get(person=viewer)
            if profile in viewer.hcw_v.all():
                #show all documents uploaded by profile of viewer
                pass
            else:
                return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))



def notifications(request):
    if request.method == "POST":

        if request.user.is_authenticated:
            body = json.loads(request.body)
            if body['type'] == "send":
                receiver_id = body['to']
                sender_division = body['as']
                payload = "approval"
                if request.user.division.lower() != sender_division.lower():
                    return HttpResponse("Forgery")
                if len(request.user.username) != 12:  # This implies that user is a normal user
                    print("Nou")
                    sender = User.objects.get(username=request.user.username)
                    receiver = User.objects.get(username=receiver_id)
                    notification = Notification(sender=sender, receiver=receiver, content=payload)
                    notification.save()
                    sender = Patients.objects.get(person=sender)
                    receiver = MedWorkerRep.objects.get(account=receiver)
                else:
                    # We can use division logic here, ill do it later. First ill finish doctor logic
                    sender = User.objects.get(username=request.user.username)
                    receiver = User.objects.get(username=receiver_id)
                    notification = Notification(sender=sender, receiver=receiver, content=payload)
                    notification.save()
                    sender = MedWorkerRep.objects.get(account=sender)
                    receiver = Patients.objects.get(person=receiver)

                receiver.notifications.add(notification)
                receiver.save()

                return HttpResponse("Nice")
            elif body['type'] == "receive":
                if request.user.division.lower() != "nou":
                    raise NotImplementedError("Will do this after implementing for nou")
                else:
                    patient = Patients.objects.get(person=User.objects.get(username=request.user))
                    notifs = patient.notifications
                    for n in notifs.all():
                        print(n.content, n.sender, n.receiver)
                    return HttpResponse("Works So far")

        else:
            print("Not authenticated")
            return HttpResponse("Nice")


def test(request):
    ctx = {"division": request.user.division, "my_id": request.user.username}
    return render(request, "health_tracker/copy_stuff_from_here.html", context=ctx)
