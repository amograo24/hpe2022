from django.contrib import admin
from .models import User, Patients, MedWorkerRep
# Register your models here.

admin.site.register(User)
admin.site.register(MedWorkerRep)
admin.site.register(Patients)