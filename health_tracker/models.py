from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
# from .models import Patients
# Create your models here.

# make a "profile" table?

class User(AbstractUser):
    # here add wbid
    # wbid=models.CharField(max_length=16,min_length=12,default=None)
    # full_name = models.CharField(default=None, max_length=200, verbose_name="Full Name",null=True,blank=True)
    division_choices = [
        ('D/HCW/MS', 'Doctor/Health Care Worker/Medical Staff'),
        ('I/SP', 'Insurance/Health Service Provider'),
        ('MSh', 'Medical Shop'),
        ('NoU','Normal User')
        ]
    division=models.CharField(default='NoU',max_length=20,choices=division_choices,verbose_name="Division",null=True,blank=True)
    # wbid=models.CharField(default=None,verbose_name="Well-Being ID",max_length=16,validators=[MinLengthValidator(12)],unique=True)
    # aadharid=models.CharField(default=None,verbose_name="Aadhar ID",max_length=12,validators=[MinLengthValidator(12)],unique=True)
    # reg_no=models.CharField(default=None,max_length=20,verbose_name="Registration No./License ID")
    # department=models.CharField(default=None,max_length=100)
    # image field

class MedWorkerRep(models.Model):
    full_com_name=models.CharField(default=None, max_length=200, verbose_name="Full Name/Company Name")
    # division=models.CharField(default=None,max_length=20,choices=division_choices,verbose_name="Do any of the following apply to you",blank=True)
    department=models.CharField(default=None,max_length=100,null=True,blank=True) #give choices
    reg_no=models.CharField(default=None,max_length=20,verbose_name="Registration No./License ID")
    hcwvid=models.CharField(default=None,max_length=11,validators=[MinLengthValidator(11)],verbose_name="Health Care Worker/Vendor ID",unique=True)
    account=models.ForeignKey(User,on_delete=models.CASCADE,related_name="account",default=None)
    # customers=models.ManyToManyField(Patients,blank=True,related_name='customers')
    def __str__(self):
        return f"{self.account}"
    
    class Meta:
        verbose_name_plural='Medical Workers/Insurance Representives/Pharmaceutical Shops'

class Patients(models.Model):
    full_name=models.CharField(default=None, max_length=200, verbose_name="Full Name")
    person=models.ForeignKey(User,on_delete=models.CASCADE,related_name="person",default=None)
    wbid=models.CharField(default=None,verbose_name="Well-Being ID",max_length=16,validators=[MinLengthValidator(12)],unique=True)
    aadharid=models.CharField(default=None,verbose_name="Aadhar ID",max_length=12,validators=[MinLengthValidator(12)],unique=True)
    hcw_v=models.ManyToManyField(MedWorkerRep,blank=True,related_name='hcw_v')
    
    def __str__(self):
        return f"{self.person}"
    
    class Meta:
        verbose_name_plural='Patients'
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


class Notification(models.Model):
    sender = models.CharField(max_length=200, verbose_name="Sender's Name")
    receiver = models.CharField(max_length=16, verbose_name="Receiver's Name")
    content = models.CharField(max_length=200, verbose_name="Message Content")