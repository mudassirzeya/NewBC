from django.contrib import admin
from .models import UserProfile, ZenotiCentersData, ZenotiEmployeesData, SecretKeyModel, ExtendedZenotiEmployeesData, AssociatedRoleOptions, WeekOffOptions, ExtendedZenotiCenterData, EmployeesLeaveData, KRADesignation, SLRSalonAuditAccess, KRACategory, UserTypes, SlrAudit, SlrDetail, SlrSalonImages, AuditAccess, MonthAudit, CentralAccess, AuditTypes, KRA, CenterKra, Location
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ZenotiCentersData)
admin.site.register(CenterKra)
admin.site.register(ZenotiEmployeesData)
admin.site.register(SecretKeyModel)
admin.site.register(ExtendedZenotiEmployeesData)
admin.site.register(AssociatedRoleOptions)
admin.site.register(WeekOffOptions)
admin.site.register(ExtendedZenotiCenterData)
admin.site.register(EmployeesLeaveData)
admin.site.register(KRACategory)
admin.site.register(KRADesignation)
admin.site.register(KRA)
admin.site.register(UserTypes)
admin.site.register(AuditAccess)
admin.site.register(SLRSalonAuditAccess)
admin.site.register(SlrAudit)
admin.site.register(SlrDetail)
admin.site.register(SlrSalonImages)
admin.site.register(MonthAudit)
admin.site.register(CentralAccess)
admin.site.register(AuditTypes)
admin.site.register(Location)
