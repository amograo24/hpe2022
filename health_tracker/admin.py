from django.contrib import admin
from .models import User, Patients, MedWorkerRep, Notification, Files
# Register your models here.

admin.site.register(User)
admin.site.register(MedWorkerRep)
admin.site.register(Patients)
admin.site.register(Notification)
admin.site.register(Files)