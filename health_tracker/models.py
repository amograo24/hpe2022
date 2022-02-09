from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
# Create your models here.

# make a "profile" table?

class User(AbstractUser):
    # here add wbid
    # wbid=models.CharField(max_length=16,min_length=12,default=None)
    division_choices = [
        ('D/HCW/MS', 'Doctor/Health Care Worker/Medical Staff'),
        ('I/SP', 'Insurance/Health Service Provider'),
        ('MSh', 'Medical Shop'),
        ]
    division=models.CharField(default=None,max_length=20,choices=division_choices,verbose_name="Do any of the following apply to you",blank=True)
    wbid=models.CharField(default=None,verbose_name="Well-Being ID",max_length=16,validators=[MinLengthValidator(12)],unique=True)
    aadharid=models.CharField(default=None,verbose_name="Aadhar ID",max_length=12,validators=[MinLengthValidator(12)],unique=True)
    reg_no=models.CharField(default=None,max_length=20,verbose_name="Registration No./License ID")
    department=models.CharField(default=None,max_length=100)
    # image field

# class MedWorkerRep(AbstractUser):
#     # type of the dude and stuff
#     division_choices = [
#         ('D/HCW/MS', 'Doctor/Health Care Worker/Medical Staff'),
#         ('I/SP', 'Insurance/Health Service Provider'),
#         ('MSh', 'Medical Shop'),
#         ]
#     division=models.CharField(default=None,choices=division_choices,verbose_name="Sector")
#     reg_no=models.CharField(default=None,verbose_name="Registration No./License ID")
#     patients_customers=models.ManyToManyField(User,blank=True,related_name="patients_customers",verbose_name="Patients/Customers")
#     pass
