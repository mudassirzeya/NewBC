from django.contrib import admin
from .models import EmployeeRoster, EmployeeScheduler, ErrorLog
# Register your models here.
admin.site.register(EmployeeRoster)
admin.site.register(EmployeeScheduler)
admin.site.register(ErrorLog)
