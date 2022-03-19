from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils import timezone


# from .models import Patients
# Create your models here.

# make a "profile" table?


class User(AbstractUser):
    division_choices = [
        ('D/HCW/MS', 'Doctor/Health Care Worker/Medical Staff'),
        ('I/SP', 'Insurance/Health Service Provider'),
        ('MSh', 'Medical Shop/Lab'),
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
    date_of_approval = models.DateTimeField(default=timezone.now)
    # status field to check whether it is approved or not


class MedWorkerRep(models.Model):
    full_com_name = models.CharField(default=None, max_length=200, verbose_name="Full Name/Company Name")
    department = models.CharField(default=None, max_length=100, null=True, blank=True)  # only for doctors
    reg_no = models.CharField(default=None, max_length=20, verbose_name="Registration No./License ID")
    hcwvid = models.CharField(default=None, max_length=11, validators=[MinLengthValidator(11)],
                              verbose_name="Health Care Worker/Vendor ID", unique=True)
    account = models.ForeignKey(User, on_delete=models.CASCADE, related_name="account", default=None)
    notifications = models.ManyToManyField(Notification, related_name="mwr_notifs", blank=True)
    public = models.BooleanField(default=False)
    address = models.CharField(default=None, max_length=500, verbose_name="Address", blank=True, null=True)
    city = models.CharField(default=None, max_length=100, verbose_name="City/Town", blank=True, null=True)
    state = models.CharField(default=None, max_length=100, verbose_name="State/Union Territory", blank=True, null=True)
    pincode = models.CharField(default=None, max_length=6, validators=[MinLengthValidator(6)], blank=True, null=True)

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


class Files(models.Model):  # SET('Deleted User')
    file_type_choices = [
        ('PRSCN', 'Prescription'),
        ('S/T', 'Schedule/Timetable'),
        ('HR/TR', 'Health Report/Test Report'),
        ('INVCE', 'Invoice'),
        ('OP', 'Operative Report'),
        ('DS', 'Discharge Summary'),
        ('MSC', 'Miscellaneous')
    ]
    uploader = models.ForeignKey(MedWorkerRep, on_delete=models.SET_NULL, null=True, related_name="uploader",
                                 default=None, verbose_name="Uploaded By")
    recipent = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name="recipent", default=None,
                                 verbose_name="Recipent")
    tags = models.CharField(default=None, blank=True, null=True, verbose_name="Tags/Keywords", max_length=200)
    file = models.FileField(default=None, unique=True, verbose_name="File Path")
    vendor_name = models.CharField(default=None, blank=True, null=True,
                                   verbose_name="Name of person uploading this document", max_length=200)
    date = models.DateTimeField(default=timezone.now)
    file_type = models.CharField(default='MSC', max_length=20, choices=file_type_choices, verbose_name="File Type")

    # remarks and type

    def __str__(self):
        return f"{self.file}"


class HealthStatus(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name="patient", verbose_name="Patient",
                                default=None)
    last_updated_by = models.ForeignKey(MedWorkerRep, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name="last_updated_by", verbose_name="Last Updated By")
    last_updated = models.DateTimeField(default=timezone.now)

    # lcb=models.ForeignKey(MedWorkerRep,on_delete=models.CASCADE,related)

    def __str__(self):
        return f"{self.patient}"


class HealthValue(models.Model):
    condition_category_choices = [
        ('', '----'),
        ('SAFE', 'Safe'),
        ('WARNING', 'Warning'),
        ('DANGER', 'Danger'),
        ('BDL-SAFE', 'Borderline-Safe'),
        ('BDL-DANGER', 'Borderline-Danger'),
        ('NA', 'Not Applicable')
    ]
    health_status = models.ForeignKey(HealthStatus, on_delete=models.CASCADE, related_name='health_status',
                                      verbose_name='Health Status', default=None)
    health_condition = models.CharField(default=None, verbose_name="Health Condition", max_length=100)
    maximum_value = models.FloatField(default=None, verbose_name="Maximum Value", null=True, blank=True)
    minimum_value = models.FloatField(default=None, verbose_name="Minimum Value", null=True, blank=True)
    patient_value = models.FloatField(default=None, verbose_name="Patient's Value")
    condition_category = models.CharField(default=None, max_length=20, choices=condition_category_choices,
                                          verbose_name="Health Condition Category")
