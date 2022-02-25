import datetime

import django
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404, FileResponse
from django.shortcuts import render
from django.urls import reverse
from .utils import gen_unique_id, get_hcw_vid, return_qr_code
from .forms import RegisterForm, LoginForm, UploadDocForm
from .models import User, MedWorkerRep, Patients, Notification, Files
import json
from django.core.files.storage import FileSystemStorage
import io
from fitz import fitz
from django.utils import timezone
import base64
import mimetypes
from django.contrib.admin.widgets import AdminDateWidget
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import time
import os


def upload_file(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # elif request.user.is_authenticated:
    uploader=User.objects.get(username=request.user)
    uploader_type=uploader.division.lower()
    if uploader_type not in ['d/hcw/ms','i/sp','msh']:
        return HttpResponseRedirect(reverse("index"))
    ctx = {}
    if request.method == "POST":
        # uploaded_file=request.FILES.get('document')
        form=UploadDocForm(request.POST)
        files=request.FILES.getlist('file_field')
        print("files",files)
        if form.is_valid() and files:
            uploader=MedWorkerRep.objects.get(account=uploader)
            patient=form.cleaned_data['patient']
            try:
                patient=Patients.objects.get(wbid=patient)
                notification=Notification.objects.filter(sender=uploader.account,receiver=patient.person).order_by('-date_of_approval')
                if notification:
                    time_condition = (timezone.now() - notification[0].date_of_approval) > datetime.timedelta(minutes=5)
                if uploader not in patient.hcw_v.all():
                    return render(request,"health_tracker/file_upload.html", {
                        "message":f"The Patient/Customer with the WBID '{patient.person.username}' has not yet authorized you to upload documents to their profile!",
                        "form":form
                    }) 
            except Patients.DoesNotExist:
                return render(request,"health_tracker/file_upload.html", {
                    "message":f"No Patient/Customer with the WBID '{patient}' exists!",
                    "form":form
                }) 
            # check if patient exists, and whether he is related to doctor
            vendor_name=form.cleaned_data['vendor_name']
            tags=form.cleaned_data['tags']
            # files=request.FILES.getlist('file_field')
            print(request.FILES)
            if uploader_type in ['i/sp','msh'] and uploader in patient.hcw_v.all() and time_condition:  # if uploader is med shop/insurance and if in the patient's approves list, and the time has exceeded
                patient.hcw_v.remove(uploader)
                patient.save()
                return render(request,"health_tracker/file_upload.html",{
                    "message":f"Uploading time has exceeded more than 5 minutes! Resend a request to '{patient.person.username}-{patient.full_name}'!",
                    "form":form
                })
            elif uploader in patient.hcw_v.all():
                for file in files:
                    fs = FileSystemStorage()
                    f = fs.save(f"{patient.person.username}/{file.name.replace(' ','_')}", file)
                    if uploader_type=='d/hcw/ms':
                        Files(uploader=uploader,recipent=patient,file=f,tags=tags,date=timezone.now()).save()
                    elif uploader_type in ['i/sp','msh']:
                        Files(uploader=uploader,recipent=patient,file=f,vendor_name=vendor_name,tags=tags,date=timezone.now()).save()
                        patient.hcw_v.remove(uploader)
                        patient.save()
                    print(f)
        else:
            return render(request,"health_tracker/file_upload.html", {
                "message":"You must upload atleast 1 file!",
                "form":form
            }) 

    return render(request, "health_tracker/file_upload.html",{
        "form":UploadDocForm()
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
                    ## new:
                    if division.lower()=='d/hcw/ms':
                        if dept.strip()=='':
                            return render(request, "health_tracker/register.html",{
                                "form":form,
                                "message":"You must enter a department name!"
                            })   
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
            "non_nou":user_type in ['d/hcw/ms','i/sp','msh'],
            # "file":'media/7977790201256379/Atomic_Physics.pdf'
        })
    else:
        return render(request,"health_tracker/index.html")

def myfiles(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user=User.objects.get(username=request.user)
    if user.division.lower()=='nou':
        user=Patients.objects.get(person=user)
        files=Files.objects.filter(recipent=user)[::-1]
        # file_names=[]
        # for file in files:

        print(list(files)) # error
        return render(request,"health_tracker/myfiles.html",{
            "files":files
        })
    # return render("health_tracker/myfiles.html")

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
                elif viewer_type=='i/sp': #no need two two types na.
                    # show all documents of profile uploaded by this i/sp
                    pass
                elif viewer_type=='msh':
                    # show all documents of profile uploaded by this msh
                    pass
            else:
                return HttpResponseRedirect(reverse("index"))
        elif profile_type in ['d/hcw/ms','i/sp','msh']:
            profile=MedWorkerRep.objects.get(account=profile)
            viewer=Patients.objects.get(person=viewer)
            if profile in viewer.hcw_v.all():
                #show all documents uploaded by profile of viewer
                pass
            else:
                return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))

# TODO Notification API - kushurox


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
                if len(request.user.username) == 16:  # This implies that user is a normal user or instead ==16
                    print("Nou")
                    sender = User.objects.get(username=request.user.username)
                    receiver = User.objects.get(username=receiver_id)
                    notification = Notification(sender=sender, receiver=receiver, content=payload)
                    notification.save()
                    sender = Patients.objects.get(person=sender)
                    receiver = MedWorkerRep.objects.get(account=receiver)
                else:
                    # We can use division logic here, ill do it later. First ill finish doctor logic
                    sender = User.objects.get(username=request.user.username) # remove username
                    receiver = User.objects.get(username=receiver_id)
                    notification = Notification(sender=sender, receiver=receiver, content=payload)
                    notification.save()
                    sender = MedWorkerRep.objects.get(account=sender)
                    receiver = Patients.objects.get(person=receiver)

                receiver.notifications.add(notification)
                receiver.save()
                return HttpResponse("Nice")

            elif body['type'] == "receive":
                print(request.user.division.lower())
                if request.user.division.lower() != "nou":
                    return JsonResponse({"no": "no"})

                else:
                    patient = Patients.objects.get(person=User.objects.get(username=request.user))
                    # notifs = patient.notifications
                    notification=Notification.objects.filter(receiver=patient.person).order_by('-date_of_approval')[0]
                    all_notifs = []
                    serialized_data = {}
                    # for n in notifs.all():
                    serialized_data['content'] = notification.content
                    serialized_data['sender'] = notification.sender.username
                    serialized_data['receiver'] = notification.receiver.username
                    serialized_data['doc']=notification.date_of_approval
                    all_notifs.append(serialized_data)

                    return JsonResponse(all_notifs, content_type="json", safe=False)
            elif body['type'] == "approval":
                approver = body['approver']
                authorised = body['authorised']
                if request.user.username.lower() != approver.lower():
                    return HttpResponse("Forgery")

                sender = User.objects.get(username=authorised)
                receiver = User.objects.get(username=approver)
                p_receiver = Patients.objects.get(person=receiver)
                mwr_sender = MedWorkerRep.objects.get(account=sender)
                notifs = Notification.objects.filter(sender=sender, receiver=receiver).order_by('-date_of_approval')
                if body['status'] == "yes":
                    print("Yes")
                    notif_obj=notifs[0]
                    notif_obj.date_of_approval = timezone.now()
                    notif_obj.save()
                    p_receiver.hcw_v.add(mwr_sender)
                    mwr_sender.save()
                return HttpResponse("Received")


        else:
            print("Not authenticated")
            return HttpResponse("Nice")

# TODO Test view - kushurox


def test(request):
    ctx = {"division": request.user.division, "my_id": request.user.username}
    return render(request, "health_tracker/copy_stuff_from_here.html", context=ctx)


def file_page(request,wbid,name):
    # check if the wbid exists
    # check if the viewer if authorised to view
    # check if file exists
    if not request.user.is_authenticated: #if dude not logged in
        return HttpResponseRedirect(reverse("login"))
    viewer=User.objects.get(username=request.user) #viewer

    if not User.objects.filter(username=wbid): #if the wbid doesn't exits
        return HttpResponseRedirect(reverse("index"))
    profile=User.objects.get(username=wbid) #wbid

    if profile.division.lower()!='nou': # if the wbid is not equal to a normal user
        return HttpResponseRedirect(reverse("index"))
    profile=Patients.objects.get(person=profile) # get the patient of the wbid

    if viewer.division.lower() not in ['d/hcw/ms','i/sp','msh'] and viewer!=profile.person: # if viewer is basically a normal user and if the viewer is not the profile
        return HttpResponseRedirect(reverse("index"))

    if viewer==profile.person: #if the viewer is the wbid (profile)
        if not os.path.exists(f'media/{wbid}/{name}'):
            raise Http404(f"'{name}' doesn't exist!")
    else:
        if viewer.division.lower() in ['d/hcw/ms','i/sp','msh']:
            vendor=MedWorkerRep.objects.get(account=viewer)
            if vendor in profile.hcw_v.all():
                if not os.path.exists(f'media/{wbid}/{name}'):
                    raise Http404(f"'{name}' doesn't exist!") 
            else:
                return HttpResponseRedirect(reverse("index"))
        
    # check if the file thing is being shown to the correct ppl
    file = open(f'media/{wbid}/{name}', 'rb')
    response = FileResponse(file)
    return response
    #check if file exists
    # url=f'media/{wbid}/{name}'
    # fp=open(url,'rb')
    # data=fp.read()
    # mime_type = mimetypes.MimeTypes().guess_type(url)
    # return render(request,"health_tracker/file_page.html",{
    #     "file":base64.b64encode(data).decode('utf-8'),
    #     "mt":mime_type[0],
    #     "wbid":wbid
    # })
    # def send_file(response):


def get_file(request, wbid, name: str):
    if request.method == "POST":
        ext = name[name.rfind(".")+1:]
        if ext == "pdf":
            pdf_file = fitz.open(f"media/{wbid}/{name}")
            f = io.BytesIO(pdf_file.load_page(0).get_pixmap().tobytes())
            f.name = f"{name}.png"
            return FileResponse(f)
        else:
            f = open(f"media/{wbid}/{name}", "rb")
            return FileResponse(f)

    ctx = {"wbid": wbid, "name": name}
    return render(request, 'health_tracker/file_page.html', ctx)

# validation if the patient exists, if so then save the file on patient's name