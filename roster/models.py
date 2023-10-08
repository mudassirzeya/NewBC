from django.db import models
from bc_app.models import ExtendedZenotiCenterData, ExtendedZenotiEmployeesData, KRA, UserProfile, Location, CenterKra

# Create your models here.


class EmployeeRoster(models.Model):
    center = models.ForeignKey(
        ExtendedZenotiCenterData, null=True, blank=True, on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        UserProfile, blank=True, null=True, on_delete=models.CASCADE)
    associated_kra = models.ForeignKey(
        KRA, blank=True, null=True, on_delete=models.CASCADE)
    associated_location = models.ForeignKey(
        Location, blank=True, null=True, on_delete=models.CASCADE)
    appoint_date = models.DateField(auto_now_add=False, null=True, blank=True)
    office_start_time = models.TimeField(max_length=100, null=True, blank=True)
    office_end_time = models.TimeField(max_length=100, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.employee) + '-' + str(self.appoint_date)


class ErrorLog(models.Model):
    employee = models.ForeignKey(
        UserProfile, blank=True, null=True, on_delete=models.CASCADE)
    page = models.CharField(max_length=200, null=True, blank=True)
    sentence = models.TextField(null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.employee) + '-' + str(self.added_date)


class EmployeeScheduler(models.Model):
    STATUS = (
        ('Available', 'Available'),
        ('Week Off', 'Week Off'),
        ('Leave Request', 'Leave Request'),
        ('Leave Approved', 'Leave Approved'),
        ('Unplanned Leave', 'Unplanned Leave'),
        ('Training/Meeting', 'Training/Meeting'),
        ('Floating Resource', 'Floating Resource'),
        ('Internal Transfer', 'Internal Transfer'),
        ('Exit', 'Exit'),
    )
    center = models.ForeignKey(
        ExtendedZenotiCenterData, null=True, blank=True, on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        UserProfile, blank=True, null=True, on_delete=models.CASCADE)
    associated_kra = models.ManyToManyField(
        KRA, blank=True)
    associated_location = models.ManyToManyField(
        Location, blank=True)
    status = models.CharField(
        max_length=200, null=True, blank=True, choices=STATUS)
    remark = models.CharField(
        max_length=500, null=True, blank=True)
    appoint_date = models.DateField(auto_now_add=False, null=True, blank=True)
    office_start_time = models.TimeField(max_length=100, null=True, blank=True)
    office_end_time = models.TimeField(max_length=100, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.employee) + '-' + str(self.appoint_date)
