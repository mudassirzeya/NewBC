from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserTypes(models.Model):
    user_type = models.CharField(max_length=100)
    # unique_id = models.CharField(max_length=10)

    def __str__(self):
        return str(self.user_type)


class AuditTypes(models.Model):
    audit_type = models.CharField(max_length=100)

    def __str__(self):
        return str(self.audit_type)


class WeekOffOptions(models.Model):
    option = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.option)


class SectionOption(models.Model):
    option = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.option)


class OperationOption(models.Model):
    option = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.option)


class Position(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    section = models.ForeignKey(
        SectionOption, null=True, blank=True, on_delete=models.CASCADE
    )
    operation = models.ForeignKey(
        OperationOption, null=True, blank=True, on_delete=models.CASCADE
    )
    start_time = models.TimeField(max_length=100, null=True, blank=True)
    end_time = models.TimeField(max_length=100, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.name)


# this center data is what we are getting from zenoti
class ZenotiCentersData(models.Model):
    zenoticenterId = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    address_1 = models.CharField(max_length=500, null=True, blank=True)
    address_2 = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.name) + '-' + str(self.code)


class ExtendedZenotiCenterData(models.Model):
    CENTRESTATUS = (
        ('Active', 'Active'),
        ('InActive', 'InActive')
    )
    zenoti_data = models.OneToOneField(
        ZenotiCentersData, null=True, blank=True, on_delete=models.CASCADE
    )
    opening_time = models.TimeField(max_length=100, null=True, blank=True)
    closing_time = models.TimeField(max_length=100, null=True, blank=True)
    closed_on = models.ManyToManyField(WeekOffOptions, blank=True)
    position = models.ManyToManyField(Position, blank=True)
    center_status = models.CharField(
        max_length=200, null=True, blank=True, default='Active', choices=CENTRESTATUS)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.zenoti_data.name)


class UserProfile(models.Model):
    ENTRANCE_TYPE = (
        ('Zenoti', 'Zenoti'),
        ('Non Zenoti', 'Non Zenoti')
    )
    USERSTATUS = (
        ('Active', 'Active'),
        ('InActive', 'InActive')
    )
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE
    )
    is_super_admin = models.BooleanField(default=False, null=True, blank=True)
    is_audit_admin = models.BooleanField(default=False, null=True, blank=True)
    profile_pic = models.ImageField(
        default="profile1.jpg", null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    user_type = models.CharField(
        max_length=100, blank=True, choices=ENTRANCE_TYPE)
    user_type_name = models.ManyToManyField(UserTypes, blank=True)
    user_status = models.CharField(
        max_length=200, null=True, blank=True, choices=USERSTATUS)
    roster_access = models.BooleanField(default=False, null=True, blank=True)
    associated_center = models.ManyToManyField(
        ExtendedZenotiCenterData, blank=True)
    associated_role = models.ManyToManyField(
        Position, blank=True)
    office_start_time = models.TimeField(max_length=100, null=True, blank=True)
    office_end_time = models.TimeField(max_length=100, null=True, blank=True)
    week_off = models.ManyToManyField(WeekOffOptions, blank=True)
    is_manager = models.BooleanField(default=False, null=True, blank=True)
    date_of_joining = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class SecretKeyModel(models.Model):
    token = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return str(self.token)

# this employee data is what we are getting from zenoti


class ZenotiEmployeesData(models.Model):
    user = models.ForeignKey(
        UserProfile, null=True, blank=True, on_delete=models.CASCADE
    )
    # zenoticenterId = models.CharField(max_length=100, null=True, blank=True)
    employee_code = models.CharField(max_length=100, null=True, blank=True)
    employee_id = models.CharField(max_length=100, null=True, blank=True)
    employee_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=500, null=True, blank=True)
    job_info = models.CharField(max_length=500, null=True, blank=True)
    zenoti_center = models.ManyToManyField(
        ZenotiCentersData, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class AssociatedRoleOptions(models.Model):
    option = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.option)


class ExtendedZenotiEmployeesData(models.Model):
    zenoti_data = models.ForeignKey(
        ZenotiEmployeesData, null=True, blank=True, on_delete=models.CASCADE
    )
    associated_center = models.ManyToManyField(
        ExtendedZenotiCenterData, blank=True)
    associated_role = models.ManyToManyField(
        Position, blank=True)
    office_start_time = models.TimeField(max_length=100, null=True, blank=True)
    office_end_time = models.TimeField(max_length=100, null=True, blank=True)
    week_off = models.ManyToManyField(WeekOffOptions, blank=True)
    is_manager = models.BooleanField(default=False, null=True, blank=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.zenoti_data.user)


class EmployeesLeaveData(models.Model):
    LEAVESTATUS = (
        ('Approved', 'Approved'),
        ('Pending', 'Pending'),
        ('Rejected', 'Rejected'),
    )
    user_profile = models.ForeignKey(
        UserProfile, null=True, blank=True, on_delete=models.CASCADE
    )
    leave_from_date = models.DateField(null=True, blank=True)
    leave_to_date = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(
        max_length=200, null=True, blank=True, choices=LEAVESTATUS)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.user_profile.user)


class EmployeeRoster(models.Model):
    center = models.ForeignKey(
        ExtendedZenotiCenterData, null=True, blank=True, on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        UserProfile, blank=True, null=True, on_delete=models.CASCADE)
    associated_role = models.ForeignKey(
        Position, blank=True, null=True, on_delete=models.CASCADE)
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
    associated_role = models.ManyToManyField(
        Position, blank=True)
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


class MonthAudit(models.Model):
    month = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.month)


class CentralAccess(models.Model):
    staff = models.ManyToManyField(
        UserProfile, blank=True)
    audit = models.ManyToManyField(AuditTypes, blank=True)
    auditor = models.ManyToManyField(
        ExtendedZenotiCenterData, blank=True, related_name='auditor_of'
    )
    project_owner = models.ManyToManyField(
        ExtendedZenotiCenterData, blank=True, related_name='project_manager_of'
    )
    audit_reviewer = models.ManyToManyField(
        ExtendedZenotiCenterData, blank=True, related_name='audit_reviewer_of'
    )
    senior_management = models.ManyToManyField(
        ExtendedZenotiCenterData, blank=True, related_name='senior_management_of'
    )

    def __str__(self):
        return str(self.staff) + ' - ' + str(self.audit)


class AuditAccess(models.Model):
    AUDIT_TYPE = (
        ('SLR Salon', 'SLR Salon'),
    )
    audit = models.CharField(max_length=200, null=True,
                             blank=True, choices=AUDIT_TYPE)
    center = models.ForeignKey(
        ExtendedZenotiCenterData, null=True, blank=True, on_delete=models.CASCADE
    )
    user_type_name = models.ForeignKey(
        UserTypes, blank=True, on_delete=models.CASCADE)
    edit_access = models.ManyToManyField(UserProfile, blank=True)
    view_access = models.ManyToManyField(
        UserProfile, related_name='view_access_user', blank=True)

    def __str__(self):
        return str(self.user_type_name.user_type)


class SLRSalonAuditAccess(models.Model):
    auditors = models.ManyToManyField(UserProfile, blank=True)

    def __str__(self):
        return str(self.auditors)


class SlrAudit(models.Model):
    is_deleted = models.BooleanField(default=False)
    added_by = models.ForeignKey(
        UserProfile, null=True, blank=True, on_delete=models.CASCADE
    )
    access_given_to = models.ManyToManyField(
        UserProfile, related_name='access_given_to', blank=True)
    center = models.ForeignKey(
        ExtendedZenotiCenterData, null=True, blank=True, on_delete=models.CASCADE
    )
    auditor_name = models.CharField(max_length=200, null=True, blank=True)
    trainer_name = models.CharField(max_length=200, null=True, blank=True)
    date_of_audit = models.DateField(auto_now_add=False, null=True, blank=True)
    month_of_audit = models.ForeignKey(MonthAudit,
                                       null=True, blank=True, on_delete=models.SET_NULL)
    auditor_action_reviewed = models.BooleanField(
        default=False, null=True, blank=True)
    om_action_reviewed = models.BooleanField(
        default=False, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.auditor_name)


class SlrDetail(models.Model):
    slr_audit = models.ForeignKey(
        SlrAudit, null=True, blank=True, on_delete=models.CASCADE
    )
    center = models.ForeignKey(
        ExtendedZenotiCenterData, null=True, blank=True,
        on_delete=models.SET_NULL)
    sequence = models.CharField(max_length=20, null=True, blank=True)
    compliance_dropdown = models.CharField(
        max_length=500, null=True, blank=True)
    month_of_audit = models.ForeignKey(MonthAudit,
                                       null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(auto_now_add=False, null=True, blank=True)
    audited_by = models.CharField(max_length=200, null=True, blank=True)
    kra_responsible = models.CharField(max_length=200, null=True, blank=True)
    protocol = models.CharField(max_length=200, null=True, blank=True)
    checklist = models.TextField(null=True, blank=True)
    methodology = models.TextField(null=True, blank=True)
    compliance = models.CharField(max_length=200, null=True, blank=True)
    compliance_category = models.CharField(
        max_length=200, null=True, blank=True)
    compliance_category_percentage = models.CharField(
        max_length=20, null=True, blank=True)
    audit_remarks = models.TextField(null=True, blank=True)
    person_responsible = models.ForeignKey(
        ExtendedZenotiEmployeesData, null=True, blank=True,
        on_delete=models.SET_NULL)
    audit_status = models.CharField(max_length=200, null=True, blank=True)
    comment_for_auditor = models.TextField(null=True, blank=True)
    action_taken_by_outlet_manager = models.CharField(
        max_length=200, null=True, blank=True)
    status_by_om = models.CharField(max_length=200, null=True, blank=True)
    remark_by_om = models.TextField(null=True, blank=True)
    action_taken_by_management = models.CharField(
        max_length=200, null=True, blank=True)
    remark_by_management = models.TextField(null=True, blank=True)
    expected_dept_intervene = models.CharField(
        max_length=200, null=True, blank=True)
    remark_by_department = models.TextField(null=True, blank=True)
    status_by_department = models.CharField(
        max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.slr_audit.center.zenoti_data.name) + str(self.sequence)


class SlrSalonImages(models.Model):
    slr_audit = models.ForeignKey(
        SlrAudit, null=True,
        blank=True, on_delete=models.CASCADE
    )
    center = models.ForeignKey(
        ExtendedZenotiCenterData, null=True, blank=True,
        on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=False, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    image = models.FileField(upload_to='media', null=True, blank=True)

    def __str__(self):
        return str(self.center.zenoti_data.display_name) + ' - ' + str(self.date)
