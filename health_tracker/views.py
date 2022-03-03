import datetime

import django
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404, FileResponse
from django.shortcuts import render
from django.urls import reverse
from .utils import gen_unique_id, get_hcw_vid, return_qr_code
from .forms import RegisterForm, LoginForm, UploadDocForm
from .models import User, MedWorkerRep, Patients, Notification, Files, HealthStatus, HealthValue
from django.forms import modelformset_factory, inlineformset_factory
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

def search(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(revrse("login"))
    search_entry=request.GET.get('q','')
    user=User.objects.get(username=request.user)
    files=None
    user_type=user.division.lower()
    if user_type=='nou':
        user=Patients.objects.get(person=user)
        files=Files.objects.filter(recipent=user)
        # associated_people=user.hcw_v.all()
    else:
        user=MedWorkerRep.objects.get(account=user)
        files=Files.objects.filter(uploader=user)
    print("files",files)
    associated_people=user.hcw_v.all()
    related_files=[]
    associated_people_list=[]
    # temp_associated_people_list=[]
    
    for person in associated_people:
        # check for dept
        if user_type=='nou':
            check_list=[person.account.username.lower(),person.full_com_name.lower(),person.reg_no.lower()]
            if not (person.department==None or not person.department.strip(' ')):
                check_list.append(person.department.lower())
            for i in check_list:
                if search_entry.lower() in i:
                    # print(search_entry.lower(),i)
                    associated_people_list.append(person)
                    break
                # else:
                #     print(i,False)
        else:
            check_list=[person.person.username.lower(),person.full_name.lower(),person.aadharid.lower()]
            # print(check_list)
            for i in check_list:
                if search_entry.lower() in i:
                    # print(search_entry.lower(),i)
                    associated_people_list.append(person)
                    break
                # else:
                #     print(i,False)
    print("associated_people_list",associated_people_list)
    for file in files:
        # check for tags, and the uploader, and vendor name. Ex tags it will show class str even if nothing exists. so do file.tags.strip(" ")
        check_list=[str(file.file).lower(),file.recipent.full_name.lower(),file.recipent.person.username.lower()]

        if file.uploader: 
            check_list.extend([file.uploader.full_com_name.lower(),file.uploader.account.username.lower()])
        # if file.vendor_name or file.vendor_name.strip(" "):
        if not (file.vendor_name==None or not file.vendor_name.strip(' ')):
            check_list.append(file.vendor_name.lower())
        # if file.tags or file.tags.strip(" "):
        if not (file.tags==None or not file.tags.strip(' ')):
            check_list.append(file.tags.lower())
        # print( not file.tags)
        # print(file.tags)
        # print(type(file.tags))
        # print(file.tags==None)
        # print('#########')
        # print(file.vendor_name)
        # print(type(file.vendor_name))
        # print(file.vendor_name==None)
        # uploader=file.uploader.account
        # if search_entry in str(file.file).lower() or search_entry in file.tags.lower() or search:
        # if search_entry.lower() in [str(file.file).lower(),file.recipent.full_name.lower(),file.uploader.full_com_name.lower(),file.recipent.person.username.lower(),file.uploader.account.username.lower(),file.vendor_name.lower(),file.tags.lower()]:
        for i in check_list:
            if search_entry.lower() in i:
                related_files.append(file)
                # break
                if user_type=='nou':
                    if file.uploader and file.uploader not in associated_people_list:
                        associated_people_list.append(file.uploader)
                else:
                    if file.recipent not in associated_people_list:
                        associated_people_list.append(file.recipent)       
                        break    
        # if search_entry.lower() in check_list:
        #     related_files.append(file)
        #     if user_type=='nou':
        #         if file.uploader not in associated_people_list:
        #             associated_people_list.append(file.uploader)
        #     else:
        #         if file.recipent not in associated_people_list:
        #             associated_people_list.append(file.recipent)
    print(related_files)
    print(associated_people_list)
    return render(request,"health_tracker/search.html",{
        "associated_people":associated_people_list,
        "related_files":related_files,
        "empty":not associated_people_list and not related_files,
        "search_entry":search_entry,
        "user_type":user_type
    })

def health_status(request, wbid):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    updater=User.objects.get(username=request.user)
    updater_type=updater.division.lower()
    if updater_type!='d/hcw/ms':
        return HttpResponseRedirect(reverse("login"))
    try:
        profile = User.objects.get(username=wbid)
        profile_type = profile.division.lower()
    except User.DoesNotExist:
        message=None
        if updater_type=='d/hcw/ms':
            message=f"Patient with the WBID '{wbid}' doesn't exist! Check your patients' list to update the Health Status Card for your patients."
        return render(request,"health_tracker/health_status.html",{
            "message":message,
            "wbid":wbid,
            "udne":User.DoesNotExist
        })    
    if profile_type!='nou':
        return render(request,"health_tracker/health_status.html",{
            "message":f"'{profile}' is not a patient! You can update/create Health Status Cards only for patients!",
            "wbid":wbid,
            "nap":profile_type!='nou'
        })   
    
    patient = Patients.objects.get(person=profile)
    updater=MedWorkerRep.objects.get(account=updater)
    if updater not in patient.hcw_v.all():
        return render(request,"health_tracker/health_status.html",{
            "message":f"Patient with the '{wbid}' has not authorised you to update/create their Health Status Card!",
            "wbid":wbid,
            "updater_not_auth":updater not in patient.hcw_v.all()
        })
    health_status = HealthStatus.objects.get(patient=patient)
    HealthValueFormset = inlineformset_factory(HealthStatus, HealthValue, fields=('health_status', 'health_condition', 'maximum_value', 'minimum_value', 'patient_value'))
    if request.method == 'POST':
        formset = HealthValueFormset(request.POST, instance=health_status)
        if formset.is_valid():
            for i in formset:
                print(i.cleaned_data.get('maximum_value'))
                data=i.cleaned_data
                if (data.get('maximum_value') and data.get('minimum_value')) and data.get('maximum_value')<data.get('minimum_value'):
                    return render(request,"health_tracker/health_status.html",{
                        "formset":formset,
                        "wbid":wbid,
                        "message":f"The minimum value cannot be greater than the maximum value for '{data.get('health_condition')}'!"
                    })
            # print(formset.maximum_value,formset.minimum_value)
            formset.save()
            health_status.last_updated_by = updater
            health_status.last_updated = timezone.now()
            health_status.save()
            return HttpResponseRedirect(reverse("index")) # return to patient's thingie
        else:
            return render(request,"health_tracker/health_status.html",{
                "formset":formset,
                "wbid":wbid,
                # "message":"The Health Condition Field and the Patient's value Field cannot be empty!"
            })
    return render(request, "health_tracker/health_status.html", {
        "formset": HealthValueFormset(instance=health_status),
        "wbid": wbid
    })


def upload_file(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # elif request.user.is_authenticated:
    uploader = User.objects.get(username=request.user)
    uploader_type = uploader.division.lower()
    if uploader_type not in ['d/hcw/ms', 'i/sp', 'msh']:
        return HttpResponseRedirect(reverse("index"))
    ctx = {}
    if request.method == "POST":
        # uploaded_file=request.FILES.get('document')
        form = UploadDocForm(request.POST)
        files = request.FILES.getlist('file_field')
        print("files", files)
        if form.is_valid() and files:
            uploader = MedWorkerRep.objects.get(account=uploader)
            patient = form.cleaned_data['patient']
            try:
                patient = Patients.objects.get(wbid=patient)
                notification = Notification.objects.filter(
                    sender=uploader.account, receiver=patient.person).order_by('-date_of_approval')
                if notification:
                    time_condition = (timezone.now(
                    ) - notification[0].date_of_approval) > datetime.timedelta(minutes=5)
                # TODO Avaneesh: The if condition is not working cause the patient.hcw_v.all() QuerySet is empty. So it always shows Patient has not authorized.
                if uploader not in patient.hcw_v.all():
                    return render(request, "health_tracker/file_upload.html", {
                        "message": f"The Patient/Customer with the WBID '{patient.person.username}' has not yet authorized you to upload documents to their profile!",
                        "form": form
                    })
            except Patients.DoesNotExist:
                return render(request, "health_tracker/file_upload.html", {
                    "message": f"No Patient/Customer with the WBID '{patient}' exists!",
                    "form": form
                })
            # check if patient exists, and whether he is related to doctor
            vendor_name = form.cleaned_data['vendor_name']
            tags = form.cleaned_data['tags']
            # files=request.FILES.getlist('file_field')
            print(request.FILES)
            # if uploader is med shop/insurance and if in the patient's approves list, and the time has exceeded
            if uploader_type in ['i/sp', 'msh'] and uploader in patient.hcw_v.all() and time_condition:
                patient.hcw_v.remove(uploader)
                patient.save()
                return render(request, "health_tracker/file_upload.html", {
                    "message": f"Uploading time has exceeded more than 5 minutes! Resend a request to '{patient.person.username}-{patient.full_name}'!",
                    "form": form
                })
            elif uploader in patient.hcw_v.all():
                for file in files:
                    fs = FileSystemStorage()
                    f = fs.save(
                        f"{patient.person.username}/{file.name.replace(' ','_')}", file)
                    if uploader_type == 'd/hcw/ms':
                        Files(uploader=uploader, recipent=patient, file=f, tags=tags, date=timezone.now()).save()
                    elif uploader_type in ['i/sp', 'msh']:
                        Files(uploader=uploader, recipent=patient, file=f, vendor_name=vendor_name, tags=tags, date=timezone.now()).save()
                        patient.hcw_v.remove(uploader)
                        patient.save()
                    print(f)
        else:
            return render(request, "health_tracker/file_upload.html", {
                "message": "You must upload atleast 1 file!",
                "form": form
            })

    return render(request, "health_tracker/file_upload.html", {
        "form": UploadDocForm()
    })


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            # Attempt to sign user in
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            # code=request.POST['code']
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "health_tracker/login.html", {
                    "form": form,
                    "message": "Invalid username and/or password."
                })
        else:
            return render(request, "health_tracker/login.html", {
                "form": form
            })
    return render(request, "health_tracker/login.html", {
        "form": LoginForm()
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    # verify aadhar number is inputted, etc
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # username=form.cleaned_data['username']
            full_name = form.cleaned_data['full_name']
            # first_name=form.cleaned_data['first_name']
            # last_name=form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            # dob=form.cleaned_data['dob']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            division = form.cleaned_data['division']

            if password != confirm_password:
                return render(request, "health_tracker/register.html", {
                    "form": form,
                    "message": "Passwords must match."
                })
            try:
               # Creating the user here
                if division.lower() == "nou" or division.lower() == None:
                    user = gen_unique_id(email=email, password=password)
                    aadharid = form.cleaned_data['aadharid']
                    if len(aadharid) != 12 or aadharid.isnumeric() == False:
                        return render(request, "health_tracker/register.html", {
                            "form": form,
                            "message": "Your Aadhar ID must have only 12 digits!"
                        })
                    # what if aadhar id already exisits?
                    # is this correct?
                    if Patients.objects.filter(aadharid=aadharid):
                        return render(request, "health_tracker/register.html", {
                            "form": form,
                            "message": "An account with this Aadhar ID already exists!"
                        })
                    print(request.user.pk, request.user, request.user.username)
                    Patients(aadharid=aadharid, full_name=full_name, wbid=user.username, person=user).save()
                    HealthStatus(patient=Patients.objects.get(person=user,aadharid=aadharid)).save()

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
                    "form": form,
                    "message": "Username already taken."
                })
            login(request, user)
            # redirect to my page
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "health_tracker/register.html", {
                "form": form
            })
    return render(request, "health_tracker/register.html", {
        "form": RegisterForm()
    })


def index(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        user_type = user.division.lower()
        image = None
        if user_type == 'nou':
            user = Patients.objects.get(person=user)
            image = return_qr_code(request.user)
        elif user_type in ['d/hcw/ms', 'i/sp', 'msh']:
            user = MedWorkerRep.objects.get(account=user)

        return render(request, "health_tracker/myprofile.html", {
            "image": image,
            "user": user,
            "nou": user_type == 'nou',
            "non_nou": user_type in ['d/hcw/ms', 'i/sp', 'msh'],
            # "file":'media/7977790201256379/Atomic_Physics.pdf'
        })
    else:
        return render(request, "health_tracker/index.html")


def myfiles(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user = User.objects.get(username=request.user)
    files = None
    user_type=user.division.lower()
    if user_type == 'nou':
        user = Patients.objects.get(person=user)
        files = Files.objects.filter(recipent=user)[::-1]
        # file_names=[]
        # for file in files:
        # print(list(files))  # error
        # return render(request, "health_tracker/myfiles.html", {
        #     "files": files
        # })
    else:
        user=MedWorkerRep.objects.get(account=user)
        files=Files.objects.filter(uploader=user)[::-1]
    return render(request, "health_tracker/myfiles.html", {
        "files": files,
        "user_type":user_type
    })
    # elif user.division.lower() in ['d/hcw/ms','i/sp','msh']:
    #     user=MedWorkerRep.objects.get(account=user)
    #     files=Files.objects.filter(uploader=user)[::-1]
    #     print(list(files)
    # return render(request,"health_tracker/myfiles.html",{
    #     "files":files
    # })
    # return render("health_tracker/myfiles.html")


def other_profile(request, id):
    if request.user.is_authenticated:
        if request.user == id:
            return HttpResponseRedirect(reverse("index"))
        viewer = User.objects.get(username=request.user)
        viewer_type = viewer.division.lower()
        try:
            profile = User.objects.get(username=id)
            profile_type = profile.division.lower()
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse("index"))
        if (viewer_type == 'nou' and profile_type == 'nou') or (viewer_type in ['d/hcw/ms', 'i/sp', 'msh'] and profile_type in ['d/hcw/ms', 'i/sp', 'msh']):
            return HttpResponseRedirect(reverse("index"))
        if profile_type == 'nou':
            profile = Patients.objects.get(person=profile)
            viewer = MedWorkerRep.objects.get(account=viewer)
            # if viewer in profile.hcw_v.all(): # even if not in, it should show na? basically filtered. # like only for
            # registered doctor it should show all, for doctors who were deleted, only their uploaded files
            files = Files.objects.filter(uploader=viewer, recipent=profile).order_by('-date')
            if viewer_type != 'd/hcw/ms':
                print(files, not files)
                if not files:
                    return HttpResponseRedirect(reverse("index"))
            elif viewer_type == 'd/hcw/ms':
                if viewer in profile.hcw_v.all():
                    files = Files.objects.filter(recipent=profile).order_by('-date')
                else:
                    if not files:
                        return HttpResponseRedirect(reverse("index"))
            return render(request, "health_tracker/other_profile.html", {
                "files": files,
                "viewer_doctor_type": viewer_type == 'd/hcw/ms',
                "profile_type": profile_type,
                "profile": profile,
                "viewer": viewer
            })
        elif profile_type in ['d/hcw/ms', 'i/sp', 'msh']:
            profile = MedWorkerRep.objects.get(account=profile)
            viewer = Patients.objects.get(person=viewer)
            files = Files.objects.filter(uploader=profile, recipent=viewer)

            if not files and profile not in viewer.hcw_v.all():
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "health_tracker/other_profile.html", {
                    "files": files,
                    "profile_doctor_type": profile_type == 'd/hcw/ms',
                    "profile_type": profile_type,
                    "profile": profile,
                    "viewer": viewer
                })
    else:
        return HttpResponseRedirect(reverse("login"))

# TODO Notification API - kushurox


def notifications(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            body = json.loads(request.body)

            if body['type'] == "send" and len(request.user.username) != 16:
                receiver_id = body['to']
                sender_division = body['as']
                payload = "approval"

                if request.user.division.lower() != sender_division.lower():
                    return HttpResponse("Forgery")

                if request.user.username == receiver_id:
                    return HttpResponse("Cannot invite yourself")

                sender = User.objects.filter(
                    username=request.user.username)  # remove username
                if sender:
                    sender = sender[0]
                else:
                    return HttpResponse("User not found")

                receiver = User.objects.filter(username=receiver_id)

                if receiver:
                    receiver = receiver[0]
                else:
                    return HttpResponse("User not found")

                if sender.division == receiver.division:
                    return HttpResponse("Cannot send to another doctor")

                sender = MedWorkerRep.objects.get(account=sender)
                receiver = Patients.objects.get(person=receiver)

                if sender in receiver.hcw_v.all():
                    return HttpResponse("Already in User's list")

                notification = Notification(
                    sender=sender, receiver=receiver, content=payload)

                notification.save()

                receiver.notifications.add(notification)
                receiver.save()

            elif body['type'] == "receive":

                if request.user.division.lower() != "nou":
                    mwr = MedWorkerRep.objects.get(
                        account=User.objects.get(username=request.user))
                    notifications = Notification.objects.filter(
                        receiver=mwr.account)
                    if notifications:
                        notifications = notifications.order_by('-date_of_approval')
                    else:
                        return JsonResponse([], content_type="json", safe=False)

                    all_notifs = []
                    for notification in notifications:
                        serialized_data = {
                            'content': notification.content,
                            'sender': notification.sender.username,
                            'receiver': notification.receiver.username,
                            'doc': f"{notification.date_of_approval.date()}"
                        }
                        all_notifs.append(serialized_data)
                    return JsonResponse(all_notifs, content_type="json", safe=False)

                else:
                    patient = Patients.objects.get(
                        person=User.objects.get(username=request.user))
                    notifications = Notification.objects.filter(
                        receiver=patient.person)
                    if notifications:
                        notifications = notifications.order_by('-date_of_approval')
                    else:
                        return JsonResponse([], content_type="json", safe=False)

                    all_notifs = []
                    for notification in notifications:
                        serialized_data = {
                            'content': notification.content,
                            'sender': notification.sender.username,
                            'receiver': notification.receiver.username,
                            'doc': f"{notification.date_of_approval.date()}, "
                                   f"{notification.date_of_approval.time().hour}:"
                                   f"{notification.date_of_approval.time().minute}:"
                                   f"{notification.date_of_approval.time().second}"
                        }
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
                notifs = Notification.objects.filter(
                    sender=sender, receiver=receiver).order_by('-date_of_approval')
                if body['status'] == "yes":
                    print("Yes")
                    notif_obj = notifs[0]
                    notif_obj.content = "approved"
                    notif_obj.date_of_approval = timezone.now()
                    notif_obj.save()
                    p_receiver.hcw_v.add(mwr_sender)
                    mwr_sender.save()

                    new_notif = Notification(sender=receiver, receiver=sender, content="approved")
                    new_notif.save()

                else:
                    print("No")
                    notif_obj = notifs[0]
                    notif_obj.content = "rejected"
                    notif_obj.date_of_approval = timezone.now()
                    notif_obj.save()

                    new_notif = Notification(sender=receiver, receiver=sender, content="rejected")
                    new_notif.save()

                return HttpResponse("Received")
            return HttpResponse("Saved Info")
        else:
            print("Not authenticated")
            return HttpResponse("Nice")

# TODO Test view - kushurox


def test(request):
    ctx = {"division": request.user.division, "my_id": request.user.username}
    return render(request, "health_tracker/copy_stuff_from_here.html", context=ctx)


def delete_file(request,wbid,name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user=User.objects.get(username=request.user)
    if user.division.lower=='nou':
        return HttpResponseRedirect(reverse("myfiles"))
    # if not User.objects.filter(username=wbid):
    #     return HttpResponseRedirect(reverse("index"))
    if not File.objects.filter(file=f"{wbid}/{name}"):
        return HttpResponseRedirect(reverse("myfiles"))
    else:
        file=File.objects.get(file=f"{wbid}/{name}")
        if file.uploader.account==user:
            if request.method=="POST":
                data=json.loads(request.body)
                if data['to_delete']=="yes":
                    # file.delete()
                    os.remove(f"media/{wbid}/{name}")
                    file.delete()
                    return JsonResponse({'status':200})
        else:
            return JsonResponse({'status':Forgery})
    # lecturer=User.objects.get(username=lecturer)
    # course_filter=Course.objects.filter(creator=lecturer)
    # course=course_filter.get(course_name=course)
    # if request.method=="POST":
    #     data = json.loads(request.body)
    #     if data['to_delete']=="yes":
    #         course.delete()
    #         return JsonResponse({'status':200})

def file_page(request, wbid, name):
    # check if the wbid exists
    # check if the viewer if authorised to view
    # check if file exists
    if not request.user.is_authenticated:  # if dude not logged in
        return HttpResponseRedirect(reverse("login"))
    viewer = User.objects.get(username=request.user)  # viewer

    if not User.objects.filter(username=wbid):  # if the wbid doesn't exits
        return HttpResponseRedirect(reverse("index"))
    profile = User.objects.get(username=wbid)  # wbid

    if profile.division.lower() != 'nou':  # if the wbid is not equal to a normal user
        return HttpResponseRedirect(reverse("index"))
    # get the patient of the wbid
    profile = Patients.objects.get(person=profile)

    # if viewer is basically a normal user and if the viewer is not the profile
    if viewer.division.lower() not in ['d/hcw/ms', 'i/sp', 'msh'] and viewer != profile.person:
        return HttpResponseRedirect(reverse("index"))

    if viewer == profile.person:  # if the viewer is the wbid (profile)
        if not os.path.exists(f'media/{wbid}/{name}'):
            raise Http404(f"'{name}' doesn't exist!")
    else:
        # Major Security Risk: Since the temporary user is a part of profile.hcw_v.all() he can view stuff. Also if he ain't in the thing, but he is the one who uplaoded the doc, he should be able to see
        if viewer.division.lower() in ['d/hcw/ms', 'i/sp', 'msh']:
            vendor = MedWorkerRep.objects.get(account=viewer)
            if vendor in profile.hcw_v.all():
                if not os.path.exists(f'media/{wbid}/{name}'):
                    raise Http404(f"'{name}' doesn't exist!")
                elif os.path.exists(f'media/{wbid}/{name}'):
                    file = Files.objects.get(file=f'{wbid}/{name}')
                    # print(file.file,str(file.file).lower())
                    # if the person who uploaded the file is not the vendor and if the vendor is not a doctor => intruder
                    if file.uploader != vendor and viewer.division.lower() != 'd/hcw/ms':
                        return HttpResponseRedirect(reverse("index"))
            else:
                if (os.path.exists(f'media/{wbid}/{name}') and Files.objects.get(file=f'{wbid}/{name}').uploader != vendor) or (not os.path.exists(f'media/{wbid}/{name}')):
                    return HttpResponseRedirect(reverse("index"))

    # check if the file thing is being shown to the correct ppl
    file = open(f'media/{wbid}/{name}', 'rb')
    response = FileResponse(file)
    return response


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


def notification_page(request):
    ctx = {
        "division": request.user.division
    }
    return render(request, "health_tracker/notifs.html", ctx)
