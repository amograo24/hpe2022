from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from .utils import gen_unique_id, get_hcw_vid, return_qr_code
from .forms import RegisterForm, LoginForm, UploadDocForm
from .models import User, MedWorkerRep, Patients, Notification
import json
from django.core.files.storage import FileSystemStorage
from django.contrib.admin.widgets import AdminDateWidget
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import time



# def test2(request):
#     return render(request,"health_tracker/test2.html",{
#         "file":'/media/7977790201256379/Atomic_Physics.pdf'
#     })

def upload_file(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # elif request.user.is_authenticated:
    user=User.objects.get(username=request.user)
    user_type=user.division.lower()
    if user_type not in ['d/hcw/ms','i/sp','msh']:
        return HttpResponseRedirect(reverse("index"))
    ctx = {}
    if request.method == "POST":
        # uploaded_file=request.FILES.get('document')
        form=UploadDocForm(request.POST)
        files=request.FILES.getlist('file_field')
        print("files",files)
        if form.is_valid() and files:
            patient=form.cleaned_data['patient']
            patient=Patients.objects.get(wbid=patient)
            # check if patient exists, and whether he is related to doctor
            vendor_name=form.cleaned_data['vendor_name']
            # files=request.FILES.getlist('file_field')
            print(request.FILES)
            for file in files:
                fs = FileSystemStorage()
                f = fs.save(f"{patient.person.username}/{file.name}", file)
                print(f)
        else:
            return render(request,"health_tracker/file_upload.html", {
                "message":"You must upload atleast 1 file!",
                "form":form
            }) 

    return render(request, "health_tracker/file_upload.html",{
        "form":UploadDocForm()
    })

# def upload_file(request):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("login"))
#     # elif request.user.is_authenticated:
#     user=User.objects.get(username=request.user)
#     user_type=user.division.lower()
#     if user_type not in ['d/hcw/ms','i/sp','msh']:
#         return HttpResponseRedirect(reverse("index"))
#     ctx = {}
#     if request.method == "POST":
#         uploaded_file=request.FILES.get('document')
#         form=UploadDocForm(request.POST)
#         if form.is_valid() and uploaded_file:
#             patient=form.cleaned_data['patient']
            
#             fs = FileSystemStorage()
#             f = fs.save(f"{request.user.username}/{uploaded_file.name}", uploaded_file)

#     return render(request, "health_tracker/forms_test.html", context=ctx)
    # return HttpResponse("Not Implemented Yet")

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
                print(request.user.division.lower())
                if request.user.division.lower() != "nou":
                    raise NotImplementedError("Will do this after implementing for nou")
                else:
                    patient = Patients.objects.get(person=User.objects.get(username=request.user))
                    notifs = patient.notifications
                    all_notifs = []
                    serialized_data = {}
                    for n in notifs.all():
                        serialized_data['content'] = n.content
                        serialized_data['sender'] = n.sender.username
                        serialized_data['receiver'] = n.receiver.username
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
                notifs = Notification.objects.filter(sender=sender, receiver=receiver)
                if body['status'] == "yes":
                    print("Yes")
                    p_receiver.hcw_v.add(mwr_sender)
                for n in notifs:
                    p_receiver.notifications.remove(n)
                    n.delete()
                return HttpResponse("Received")


        else:
            print("Not authenticated")
            return HttpResponse("Nice")

# TODO Test view - kushurox


def test(request):
    ctx = {"division": request.user.division, "my_id": request.user.username}
    return render(request, "health_tracker/copy_stuff_from_here.html", context=ctx)


def test_forms(request):
    ctx = {}
    if request.method == "POST":

        uploaded_file = request.FILES.get('kushurox')

        if request.user.is_authenticated and uploaded_file:
            fs = FileSystemStorage()
            f = fs.save(f"{request.user.username}/{uploaded_file.name}", uploaded_file)

    return render(request, "health_tracker/forms_test.html", context=ctx)
#validation if the patient exists, if so then save the file on patient's name