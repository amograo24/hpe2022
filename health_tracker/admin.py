from django.contrib import admin
from .models import User, Patients, MedWorkerRep, Notification, Files, HealthStatus, HealthValue
# Register your models here.

class HealthValueInline(admin.StackedInline):
    model = HealthValue

class HealthStatusAdmin(admin.ModelAdmin):
    inlines = [HealthValueInline]

admin.site.register(User)
admin.site.register(MedWorkerRep)
admin.site.register(Patients)
admin.site.register(Notification)
admin.site.register(Files)
admin.site.register(HealthStatus,HealthStatusAdmin)
admin.site.register(HealthValue)