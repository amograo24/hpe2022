from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
import datetime


# from .models import Patients
# Create your models here.

# make a "profile" table?


class User(AbstractUser):
    division_choices = [
        ('D/HCW/MS', 'Doctor/Health Care Worker/Medical Staff'),
        ('I/SP', 'Insurance/Health Service Provider'),
        ('MSh', 'Medical Shop'),
        ('NoU', 'Normal User')
    ]
    division = models.CharField(default='NoU', max_length=20, choices=division_choices, verbose_name="Division",
                                null=True, blank=True)


class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender", default=None,
                               verbose_name="Sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver", default=None,
                                 verbose_name="Receiver")
    content = models.CharField(max_length=200, verbose_name="Message Content")


class MedWorkerRep(models.Model):
    full_com_name = models.CharField(default=None, max_length=200, verbose_name="Full Name/Company Name")
    department = models.CharField(default=None, max_length=100, null=True, blank=True)  # give choices
    reg_no = models.CharField(default=None, max_length=20, verbose_name="Registration No./License ID")
    hcwvid = models.CharField(default=None, max_length=11, validators=[MinLengthValidator(11)],
                              verbose_name="Health Care Worker/Vendor ID", unique=True)
    account = models.ForeignKey(User, on_delete=models.CASCADE, related_name="account", default=None)
    notifications = models.ManyToManyField(Notification, related_name="mwr_notifs", blank=True)
    date_of_approval = models.DateTimeField(default=datetime.datetime.now())
    def __str__(self):
        return f"{self.account}"

    class Meta:
        verbose_name_plural = 'Medical Workers/Insurance Representives/Pharmaceutical Shops'


class Patients(models.Model):
    full_name = models.CharField(default=None, max_length=200, verbose_name="Full Name")
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="person", default=None)
    wbid = models.CharField(default=None, verbose_name="Well-Being ID", max_length=16,
                            validators=[MinLengthValidator(16)], unique=True)
    aadharid = models.CharField(default=None, verbose_name="Aadhar ID", max_length=12,
                                validators=[MinLengthValidator(12)], unique=True)
    hcw_v = models.ManyToManyField(MedWorkerRep, blank=True, related_name='hcw_v')
    notifications = models.ManyToManyField(Notification, related_name="p_notifs", blank=True)

    def __str__(self):
        return f"{self.person}"

    class Meta:
        verbose_name_plural = 'Patients'


class Files(models.Model):
    uploader = models.ForeignKey(MedWorkerRep, on_delete=models.CASCADE, related_name="uploader", default=None,
                                 verbose_name="Uploaded By")
    recipent = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name="recipent", default=None,
                                 verbose_name="Recipent")
    tags = models.CharField(default=None, blank=True, null=True, verbose_name="Tags/Keywords", max_length=200)
    file = models.FileField(default=None, unique=True, verbose_name="File Path")
    vendor_name = models.CharField(default=None, blank=True, null=True,
                                   verbose_name="Name of person uploading this documen", max_length=200)
    date = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return f"{self.file}"
