import datetime
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404, FileResponse
from django.shortcuts import render
from django.urls import reverse

from .mvc import NotificationManager, StateManager
from .utils import gen_unique_id, get_hcw_vid, return_qr_code, is_valid_file, sort_files, filter_files
from .forms import RegisterForm, LoginForm, UploadDocForm, EditFileForm, GoPublicForm
from .models import User, MedWorkerRep, Patients, Notification, Files, HealthStatus, HealthValue
from django.forms import inlineformset_factory
import json
from django.core.files.storage import FileSystemStorage
import io
from fitz import fitz
from django.utils import timezone
import pickle
import base64
import mimetypes
from django.contrib.admin.widgets import AdminDateWidget
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import time
import os

with open("states.pickle", "rb") as fp:
    STATES = dict(pickle.load(fp))
    sm = StateManager(STATES)


def search(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    search_entry = request.GET.get('q', '')
    user = User.objects.get(username=request.user)
    files = None
    user_type = user.division.lower()
    if user_type == 'nou':
        user = Patients.objects.get(person=user)
        files = Files.objects.filter(recipent=user)
        # associated_people=user.hcw_v.all()
    else:
        user = MedWorkerRep.objects.get(account=user)
        files = Files.objects.filter(uploader=user)
    print("files", files)
    associated_people = user.hcw_v.all()
    related_files = []
    associated_people_list = []

    for person in associated_people:
        # check for dept
        if user_type == 'nou':
            check_list = [person.account.username.lower(), person.full_com_name.lower(), person.reg_no.lower()]
            if not (person.department == None or not person.department.strip(' ')):
                check_list.append(person.department.lower())
            for i in check_list:
                if search_entry.lower() in i:
                    associated_people_list.append(person)
                    break
        else:
            check_list = [person.person.username.lower(), person.full_name.lower(), person.aadharid.lower()]
            for i in check_list:
                if search_entry.lower() in i:
                    associated_people_list.append(person)
                    break
    print("associated_people_list", associated_people_list)
    for file in files:
        # check for tags, and the uploader, and vendor name. Ex tags it will show class str even if nothing exists. so do file.tags.strip(" ")
        # check_list=[str(file.file).lower(),file.recipent.full_name.lower(),file.recipent.person.username.lower(),file.file_type.lower(),"presctiption","schedule/timetable","health report/test report","invoice","operative report","discharge summary","miscellaneous"]
        file_type_choices = [
            ('PRSCN', 'Prescription'),
            ('S/T', 'Schedule/Timetable'),
            ('HR/TR', 'Health Report/Test Report'),
            ('INVCE', 'Invoice'),
            ('OP', 'Operative Report'),
            ('DS', 'Discharge Summary'),
            ('MSC', 'Miscellaneous')
        ]
        file_category = dict(file_type_choices)[file.file_type]

        check_list = [str(file.file).lower(), file.recipent.full_name.lower(), file.recipent.person.username.lower(),
                      file.file_type.lower(), file_category.lower()]
        if file.uploader:
            check_list.extend([file.uploader.full_com_name.lower(), file.uploader.account.username.lower()])
        if not (file.vendor_name == None or not file.vendor_name.strip(' ')):
            check_list.append(file.vendor_name.lower())
        if not (file.tags == None or not file.tags.strip(' ')):
            check_list.append(file.tags.lower())
        for i in check_list:
            if search_entry.lower() in i:
                related_files.append(file)
                if user_type == 'nou':
                    if file.uploader and file.uploader not in associated_people_list:
                        associated_people_list.append(file.uploader)
                else:
                    if file.recipent not in associated_people_list:
                        associated_people_list.append(file.recipent)
                        break
    print(related_files)
    print(associated_people_list)
    return render(request, "health_tracker/search.html", {
        "associated_people": list(set(associated_people_list)),
        "related_files": list(set(related_files)),
        "empty": not associated_people_list and not related_files,
        "search_entry": search_entry,
        "user_type": user_type,
        "user": user
    })


def health_status_function(request, wbid):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    updater = User.objects.get(username=request.user)
    updater_type = updater.division.lower()
    if updater_type != 'd/hcw/ms':
        return HttpResponseRedirect(reverse("index"))
    try:
        profile = User.objects.get(username=wbid)
        profile_type = profile.division.lower()
    except User.DoesNotExist:
        message = None
        if updater_type == 'd/hcw/ms':
            message = f"Patient with the WBID '{wbid}' doesn't exist! Check your patients' list to update the Health Status Card for your patients."
        return render(request, "health_tracker/health_status.html", {
            "message": message,
            "wbid": wbid,
            "udne": User.DoesNotExist
        })
    if profile_type != 'nou':
        print("Bug Trigger 2")
        return render(request, "health_tracker/health_status.html", {
            "message": f"'{profile}' is not a patient! You can update/create Health Status Cards only for patients!",
            "wbid": wbid,
            "nap": profile_type != 'nou'
        })

    patient = Patients.objects.get(person=profile)
    updater = MedWorkerRep.objects.get(account=updater)
    if updater not in patient.hcw_v.all():
        print("Bug Trigger!")
        return render(request, "health_tracker/health_status.html", {
            "message": f"Patient with the '{wbid}' has not authorised you to update/create their Health Status Card!",
            "wbid": wbid,
            "updater_not_auth": updater not in patient.hcw_v.all(),
        })

    health_status = HealthStatus.objects.get(patient=patient)
    HealthValueFormset = inlineformset_factory(HealthStatus, HealthValue, fields=('health_status', 'health_condition',
                                                                                  'maximum_value', 'minimum_value',
                                                                                  'patient_value',
                                                                                  'condition_category'), extra=1)
    if request.method == 'POST':
        print(request.POST)
        formset = HealthValueFormset(request.POST, instance=health_status)
        # print(formset.errors, formset)
        if formset.is_valid():
            print("formset:", formset)
            for i in formset:
                print("FormsetLoop Running")
                print(i.cleaned_data.get('maximum_value'))
                data = i.cleaned_data
                if (data.get('maximum_value') and data.get('minimum_value')) and data.get('maximum_value') < data.get(
                        'minimum_value'):
                    return render(request, "health_tracker/health_status.html", {
                        "formset": formset,
                        "wbid": wbid,
                        "message": f"The minimum value cannot be greater than the maximum value for '{data.get('health_condition')}'!"
                    })
            # print(formset.maximum_value,formset.minimum_value)
            formset.save()
            health_status.last_updated_by = updater
            health_status.last_updated = timezone.now()
            health_status.save()
            return HttpResponseRedirect(reverse("index"))  # return to patient's thingie
        else:
            print(formset.errors)
            formset = HealthValueFormset(instance=health_status)
            return render(request, "health_tracker/health_status.html", {
                "formset": formset,
                "wbid": wbid,
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
        if form.is_valid() and files:
            uploader = MedWorkerRep.objects.get(account=uploader)
            patient = form.cleaned_data['patient']

            for file in files:
                if not is_valid_file(file):
                    files.remove(file)
                    print(file)
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
                        "message": f"The Patient/Customer with the WBID {patient.person.username} has not yet authorized you to upload documents to their profile!",
                        "form": form,
                        "division": request.user.division
                    })
            except Patients.DoesNotExist:
                return render(request, "health_tracker/file_upload.html", {
                    "message": f"No Patient/Customer with the WBID '{patient}' exists!",
                    "form": form,
                    "division": request.user.division
                })
            # check if patient exists, and whether he is related to doctor
            vendor_name = form.cleaned_data['vendor_name']
            file_type = form.cleaned_data['file_type']
            tags = form.cleaned_data['tags']
            # if uploader is med shop/insurance and if in the patient's approves list, and the time has exceeded
            if uploader_type in ['i/sp', 'msh'] and uploader in patient.hcw_v.all() and time_condition:
                patient.hcw_v.remove(uploader)
                patient.save()
                return render(request, "health_tracker/file_upload.html", {
                    "message": f"Uploading time has exceeded more than 5 minutes! Resend a request to '{patient.person.username}-{patient.full_name}'!",
                    "form": form,
                    "division": request.user.division
                })
            elif uploader in patient.hcw_v.all():
                for file in files:
                    fs = FileSystemStorage()
                    f = fs.save(
                        f"{patient.person.username}/{file.name.replace(' ', '_')}", file)
                    if uploader_type == 'd/hcw/ms':
                        Files(uploader=uploader, recipent=patient, file=f, file_type=file_type, tags=tags,
                              date=timezone.now()).save()
                    elif uploader_type in ['i/sp', 'msh']:
                        Files(uploader=uploader, recipent=patient, file=f, file_type=file_type, vendor_name=vendor_name,
                              tags=tags, date=timezone.now()).save()
                        patient.hcw_v.remove(uploader)
                        patient.save()
                return HttpResponseRedirect(reverse("myfiles"))
        else:
            return render(request, "health_tracker/file_upload.html", {
                "message": "You must upload atleast 1 file!",
                "form": form,
                "division": request.user.division
            })

    return render(request, "health_tracker/file_upload.html", {
        "form": UploadDocForm(),
        "division": request.user.division
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
                    HealthStatus(patient=Patients.objects.get(person=user, aadharid=aadharid)).save()

                elif division.lower() in ['d/hcw/ms', 'i/sp', 'msh']:
                    user = get_hcw_vid(email=email, password=password, division=division)
                    reg_no = form.cleaned_data['reg_no']
                    dept = form.cleaned_data['department']
                    ## new:
                    if division.lower() == 'd/hcw/ms':
                        if dept.strip() == '':
                            return render(request, "health_tracker/register.html", {
                                "form": form,
                                "message": "You must enter a department name!"
                            })
                    MedWorkerRep(reg_no=reg_no, department=dept, full_com_name=full_name, hcwvid=user.username,
                                 account=user).save()

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
            image = return_qr_code(f"/visit/{request.user}")  # DOMAIN NAME TO BE ADDED
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
    print(request.POST)
    sort_method = request.POST.get('sort') or "def"
    filter_method = request.POST.get("filter") or "def"
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user = User.objects.get(username=request.user)
    files = None
    user_type = user.division.lower()
    if user_type == 'nou':
        user = Patients.objects.get(person=user)
        files = Files.objects.filter(recipent=user)[::-1]

    else:
        user = MedWorkerRep.objects.get(account=user)
        files = Files.objects.filter(uploader=user)[::-1]

    files = filter_files(files, filter_method)
    files = sort_files(files, sort_method)
    return render(request, "health_tracker/myfiles.html", {
        "files": files,
        "user_type": user_type
    })


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
        if (viewer_type == 'nou' and profile_type == 'nou') or (
                viewer_type in ['d/hcw/ms', 'i/sp', 'msh'] and profile_type in ['d/hcw/ms', 'i/sp', 'msh']):
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

def visit_qrcode(request, id):
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
        if (viewer_type == 'nou' and profile_type == 'nou') or (
                viewer_type in ['d/hcw/ms', 'i/sp', 'msh'] and profile_type in ['d/hcw/ms', 'i/sp', 'msh']):
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
                    if viewer not in profile.hcw_v.all():
                        return HttpResponseRedirect(reverse("auth_messages") + f"?w={profile.person.username}")
                    else:
                        return HttpResponseRedirect(reverse("index"))
            elif viewer_type == 'd/hcw/ms':
                # if viewer in profile.hcw_v.all():
                #     files = Files.objects.filter(recipent=profile).order_by('-date')
                if viewer not in profile.hcw_v.all() and not files:
                    # if not files:
                    # return HttpResponseRedirect(reverse("index"))
                    return HttpResponseRedirect(reverse("auth_messages") + f"?w={profile.person.username}")
                    # return HttpResponseRedirect(reverse("auth_messages"))
            return HttpResponseRedirect(reverse("other_profile", args=(profile.person.username,)))
        elif profile_type in ['d/hcw/ms', 'i/sp', 'msh']:
            profile = MedWorkerRep.objects.get(account=profile)
            viewer = Patients.objects.get(person=viewer)
            files = Files.objects.filter(uploader=profile, recipent=viewer)

            if not files and profile not in viewer.hcw_v.all():
                # return HttpResponseRedirect(reverse("index"))
                if profile.public == True:
                    return render(request, "health_tracker/visit_profile.html", {
                        "vendor": profile
                    })
                else:
                    return HttpResponseRedirect(reverse("index"))
            else:
                return HttpResponseRedirect(reverse("other_profile", args=(profile.account.username,)))
    else:
        return HttpResponseRedirect(reverse("login"))


def notifications(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponse("Not Authenticated")

        body = json.loads(request.body)
        sender = receiver = None

        if body['type'] == "send":
            sender = User.objects.get(username=request.user)
            receiver = User.objects.filter(username=body['to'])
            if receiver:
                receiver = receiver[0]
            else:
                return HttpResponse("Receiver Not Found")

        elif body['type'] == "receive":
            sender = User.objects.get(username=request.user)

        elif body['type'] == "approval":
            sender = User.objects.get(username=body['as'])
            receiver = User.objects.get(username=request.user)

        nm = NotificationManager(request, sender, receiver)
        return nm.validate_request()

    else:
        return HttpResponse("Get Method Not Allowed")


# TODO Test view - kushurox


def test(request):
    ctx = {"division": request.user.division, "my_id": request.user.username}
    return render(request, "health_tracker/copy_stuff_from_here.html", context=ctx)


def delete_file(request, wbid, name):
    print(wbid, name)
    print(request.body)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user = User.objects.get(username=request.user)
    if user.division.lower() == 'nou':
        return HttpResponseRedirect(reverse("myfiles"))
    # if not User.objects.filter(username=wbid):
    #     return HttpResponseRedirect(reverse("index"))
    if not Files.objects.filter(file=f"{wbid}/{name}"):
        return HttpResponseRedirect(reverse("myfiles"))
    else:
        file = Files.objects.get(file=f"{wbid}/{name}")
        if file.uploader and file.uploader.account == user:
            if request.method == "POST":
                data = json.loads(request.body)
                print(data)
                if data['to_delete'] == "yes":
                    # file.delete()
                    os.remove(f"media/{wbid}/{name}")
                    file.delete()
                    return JsonResponse({'status': 200})
            else:
                return HttpResponse('<h1>GET method is not permitted!</h1>')
        else:
            # return JsonResponse({'status':"Forgery"})
            return HttpResponse('<h1>Forgery! You can only delete the files you have uploaded!</h1>')
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
        # Major Security Risk: Since the temporary user is a part of profile.hcw_v.all() he can view stuff. Also if
        # he ain't in the thing, but he is the one who uploaded the doc, he should be able to see
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
                if (os.path.exists(f'media/{wbid}/{name}') and Files.objects.get(
                        file=f'{wbid}/{name}').uploader != vendor) or (not os.path.exists(f'media/{wbid}/{name}')):
                    return HttpResponseRedirect(reverse("index"))

    # check if the file thing is being shown to the correct ppl
    file = open(f'media/{wbid}/{name}', 'rb')
    response = FileResponse(file)
    return response


def get_file(request, wbid, name: str):
    if request.method == "POST":
        ext = name[name.rfind(".") + 1:]
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
        "division": request.user.division,
        "default_wbid": request.GET.get('w', '')
    }
    return render(request, "health_tracker/notifs.html", ctx)


def mydoctors_vendors(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user = User.objects.get(username=request.user)
    if user.division.lower() != 'nou':
        return HttpResponseRedirect(reverse("mypatients_customers"))
    patient = Patients.objects.get(person=user)
    files = Files.objects.filter(recipent=patient)
    authorized_doctors = []
    other_doctors = []
    insurance_service_providers = []
    medical_shops_labs = []
    for doctor in patient.hcw_v.all():
        if doctor.account.division.lower() == 'd/hcw/ms':
            if doctor not in authorized_doctors:
                authorized_doctors.append(doctor)

    for file in files:
        if file.uploader and file.uploader not in patient.hcw_v.all():
            vendor_type = file.uploader.account.division.lower()
            if vendor_type == 'd/hcw/ms' and file.uploader not in other_doctors:
                other_doctors.append(file.uploader)
            elif vendor_type == 'i/sp' and file.uploader not in insurance_service_providers:
                insurance_service_providers.append(file.uploader)
            elif vendor_type == 'msh' and file.uploader not in medical_shops_labs:
                medical_shops_labs.append(file.uploader)

    return render(request, "health_tracker/mydoctors_vendors.html", {
        "authorized_doctors": authorized_doctors,
        "other_doctors": other_doctors,
        "insurance_service_providers": insurance_service_providers,
        "medical_shops_labs": medical_shops_labs
    })


def mypatients_customers(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user = User.objects.get(username=request.user)
    if user.division.lower() == 'nou':
        return HttpResponseRedirect(reverse("mypatients_customers"))
    vendor = MedWorkerRep.objects.get(account=user)
    patients_customers = []
    files = Files.objects.filter(uploader=vendor)
    # customers=[]    
    # if venoder.account.division.lower()=='d/hcw/ms':
    for patient in vendor.hcw_v.all():
        patients_customers.append(patient)
    for file in files:
        if file.recipent not in patients_customers:
            patients_customers.append(file.recipent)
    return render(request, "health_tracker/mypatients_customers.html", {
        "patients_customers": patients_customers,
        "vendor": vendor
    })


def edit_file(request, wbid, file_name):
    ##############################################
    if not request.user.is_authenticated:  # if user not authenticated
        return HttpResponseRedirect(reverse("login"))
    editor = User.objects.get(username=request.user)
    # editor_type=editor.division.lower()
    if editor.division.lower() == 'nou':
        return HttpResponseRedirect(reverse("file_page", args=[wbid, file_name]))  # it will do by itself na?
    if not User.objects.filter(username=wbid):  # if the wbid doesn't exist
        # if editor_type=='nou':
        #     return HttpResponseRedirect(reverse("mydoctors_vendors"))
        # else:
        return HttpResponseRedirect(reverse("mypatients_customers"))
    profile = User.objects.get(username=wbid)

    # if editor.division.lower()=='nou':
    #     return HttpResponseRedirect(reverse("file_page",args=[wbid,file_name]))

    if profile.division.lower() != 'nou':  # if the wbid is not a normal user, ie /hcwvid/file_name
        return HttpResponseRedirect(reverse("index"))
    profile = Patients.objects.get(person=profile)

    editor = MedWorkerRep.objects.get(account=editor)
    # check if file path exists. If it exists, then we have to check if the uploader is the editor, if so give access, else redirect
    files = Files.objects.filter(uploader=editor, recipent=profile)  # /1/haha, /1/kaka
    if not files:
        return HttpResponseRedirect(reverse("other_profile", args=[wbid]))
    if not os.path.exists(
            f'media/{wbid}/{file_name}'):  # basically if the doctor and patient are related, it should tell them that the filename doesn't exist na
        # if not os.path.exists(f'media/{wbid}/{name}'):
        raise Http404(f"'{file_name}' doesn't exist!")
    # if no files, then it redirects. So basically, if files exist, then
    file = Files.objects.get(file=f'{wbid}/{file_name}', uploader=editor, recipent=profile)

    form0 = EditFileForm(initial={'tags': file.tags, 'vendor_name': file.vendor_name, 'file_type': file.file_type})
    # print(form0(initial={'tags':file.tags}))
    # form0.fields['tags']=file.tags # what if it is null?
    # form0.fields['vendor_name']=file.vendor_name # what if it is null?
    # form0.fields['file_type']=file.file_type
    if request.method == "POST":
        form = EditFileForm(request.POST)
        if form.is_valid():
            # tags=form.cleaned_data['tags']
            # vendor_name=form.cleaned_data['vendor_name']
            # file_type=form.cleaned_data['file_type']
            print(form.cleaned_data)
            file.tags = form.cleaned_data['tags']
            file.vendor_name = form.cleaned_data['vendor_name']
            file.file_type = form.cleaned_data['file_type']
            file.save()
            return HttpResponseRedirect(reverse("myfiles"))
        else:
            return render(request, "health_tracker/edit_file.html", {
                "form": form,
                "wbid": wbid,
                "file_name": file_name
            })
    return render(request, "health_tracker/edit_file.html", {
        "form": form0,
        "wbid": wbid,
        "file_name": file_name
    })


def go_public(request):
    global sm
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user = User.objects.get(username=request.user)
    if user.division.lower() == 'nou':
        return HttpResponseRedirect(reverse("index"))
    vendor = MedWorkerRep.objects.get(account=user)
    form0 = GoPublicForm(initial={'address': vendor.address, 'pincode': vendor.pincode})
    if request.method == "POST":

        form = GoPublicForm(request.POST)
        if form.is_valid():
            vendor.address = form.cleaned_data['address']
            vendor.city = request.POST['district']
            vendor.state = request.POST['state']
            vendor.pincode = form.cleaned_data['pincode']
            vendor.public = True
            vendor.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "health_tracker/go_public.html", {
                "form": form,
                "vendor": vendor,
                "states": sm.get_states()
            })
    return render(request, "health_tracker/go_public.html", {
        "form": form0,
        "vendor": vendor,
        "states": sm.get_states()
    })


def go_private(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user = User.objects.get(username=request.user)
    if user.division.lower() == 'nou':
        return HttpResponseRedirect(reverse("index"))
    vendor = MedWorkerRep.objects.get(account=user)
    # if vendor.public!=True:
    #     return HttpResponseRedirect(reverse("index"))
    vendor.public = False
    vendor.save()
    return HttpResponseRedirect(reverse("index"))


def search_public_vendors(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    search_entry = request.GET.get('q', '')
    user = User.objects.get(username=request.user)
    public_doctors = []
    public_insurance_service_providers = []
    public_medical_shops_labs = []
    public_vendors = MedWorkerRep.objects.filter(public=True)
    check_list = []
    for vendor in public_vendors:
        check_list = [vendor.account.username.lower(), vendor.full_com_name.lower(), vendor.reg_no.lower()]
        if not (vendor.department == None or not vendor.department.strip(' ')):
            check_list.append(vendor.department.lower())
        if not (vendor.address == None or not vendor.address.strip(' ')):
            check_list.append(vendor.address.lower())
        if not (vendor.city == None or not vendor.city.strip(' ')):
            check_list.append(vendor.city.lower())
        if not (vendor.state == None or not vendor.state.strip(' ')):
            check_list.append(vendor.state.lower())
        if not (vendor.pincode == None or not vendor.pincode.strip(' ')):
            check_list.append(vendor.pincode.lower())
        for i in check_list:
            if search_entry.lower() in i:
                if vendor.account.division.lower() == 'd/hcw/ms':
                    public_doctors.append(vendor)
                elif vendor.account.division.lower() == 'i/sp':
                    public_insurance_service_providers.append(vendor)
                elif vendor.account.division.lower() == 'msh':
                    public_medical_shops_labs.append(vendor)
                break
    # return render(request,"health_tracker_search_public_vendors",{
    return render(request, "health_tracker/search_public_vendors.html", {
        "search_entry": search_entry,
        "empty": not public_doctors and not public_insurance_service_providers and not public_medical_shops_labs,
        "public_doctors": sorted(set(public_doctors)),
        "public_insurance_service_providers": sorted(set(public_insurance_service_providers)),
        "public_medical_shops_labs": sorted(set(public_medical_shops_labs))
    })


def remove_patient_vendor(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user = User.objects.get(username=request.user)

    if not User.objects.filter(username=id):
        if user.division.lower() == 'nou':
            return HttpResponseRedirect(reverse("mydoctors_vendors"))
        else:
            return HttpResponseRedirect(reverse("mypatients_customers"))
    else:
        profile = User.objects.get(username=id)
        if user == profile:
            return HttpResponseRedirect(reverse("index"))
        user_type = user.division.lower()
        profile_type = profile.division.lower()
        if user_type == 'nou' and profile_type != 'nou':
            user = Patients.objects.get(person=user)
            profile = MedWorkerRep.objects.get(account=profile)
            if profile in user.hcw_v.all():
                if request.method == "POST":
                    data = json.loads(request.body)
                    print(data)
                    if data['to_delete'] == "yes":
                        user.hcw_v.remove(profile)
                        return JsonResponse({'status': 200})
                else:
                    return HttpResponse('<h1>GET method is not permitted!</h1>')
            else:
                if Files.objects.filter(uploader=profile, recipent=user):
                    return HttpResponse(
                        f"<h1>{profile.full_com_name} ({profile.account.username}) has already been removed!</h1>")
                return HttpResponseRedirect(reverse("mydoctors_vendors"))
        elif user_type != 'nou' and profile_type == 'nou':
            user = MedWorkerRep.objects.get(account=user)
            profile = Patients.objects.get(person=profile)
            if profile in user.hcw_v.all():
                if request.method == "POST":
                    data = json.loads(request.body)
                    print(data)
                    if data['to_delete'] == "yes":
                        user.hcw_v.remove(profile)
                        return JsonResponse({'status': 200})
                else:
                    return HttpResponse('<h1>GET method is not permitted!</h1>')
            else:
                if Files.objects.filter(uploader=user, recipent=profile):
                    return HttpResponse(
                        f"<h1>{profile.full_name} ({profile.person.username}) has already been removed!</h1>")
                else:
                    return HttpResponseRedirect(reverse("mypatients_customers"))
        else:
            return HttpResponse("<h1>Error, User couldn't be removed! </h1>")  # or do i redirect


def StatesAPI(request):
    global sm
    if request.method == "POST":
        body = json.loads(request.body)
        return JsonResponse(sm.get_districts(body['sn']), safe=False, content_type="json")
