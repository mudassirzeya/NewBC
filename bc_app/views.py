from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, ZenotiCentersData, ZenotiEmployeesData, SecretKeyModel, ExtendedZenotiEmployeesData, AssociatedRoleOptions, WeekOffOptions, EmployeeRoster, ExtendedZenotiCenterData, ExtendedZenotiEmployeesLeaveData, EmployeeScheduler, SectionOption, Position, OperationOption, ErrorLog, AuditAccess, SlrAudit, SLRSalonAuditAccess, SlrSalonImages, SlrDetail, MonthAudit, UserTypes, CentralAccess, AuditTypes
from mystery_shopping.models import MysteryShoppingDetail, MysteryShoppingOverview
from .forms import ExtendedZenotiDataForm, EmployeeRosterForm, ExtendedZenotiCenterDataForm, SlrAuditForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import date, timedelta, datetime
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.conf import settings
import requests
import json
import calendar
import time
import csv
import re
# email
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string

# Create your views here.
api_key = '14d874c8d968487c92b1e5b29b01e4f00261bfcc97d942efb76b7938983f91ff'


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # print("user", password, username)
        user = authenticate(request, username=username, password=password)
        # print("us", user)
        if user is not None:
            login(request, user)
            return redirect('admin_page')
        else:
            messages.info(request, 'Username or Password is in correct')
    context = {}
    return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    return redirect('user_login')


# @login_required(login_url='user_login')
# def other_user_page(request):
#     user = request.user
#     staffProfile = UserProfile.objects.get(user=user)
#     admin_user = UserProfile.objects.filter(
#         user_type='admin').exclude(user__is_superuser=True)
#     if request.method == "POST":
#         phone = request.POST.get("phone")
#         passcode = request.POST.get("passcode")
#         name = request.POST.get("name")
#         username = request.POST.get("email")
#         try:
#             already_user = User.objects.get(username=username)
#         except Exception:
#             already_user = None
#             # print('user', already_user)
#         if already_user is None:
#             new_user = User.objects.create_user(
#                 username=username, password=passcode, first_name=name)
#             UserProfile.objects.create(
#                 user=new_user,
#                 phone=phone,
#                 email=username,
#                 password=passcode,
#                 user_type='Non Zenoti',
#             )
#             return redirect('admin_team')
#         else:
#             messages.info(
#                 request, 'This Email Id is already exist in our DataBase')
#             return redirect('admin_team')
#     context = {'admin_user': admin_user, 'staffProfile': staffProfile}
#     return render(request, "admin_team.html", context)


@login_required(login_url='user_login')
def staff_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    usertype = staffProfile.user_type
    return redirect('admin_page')
    context = {'staffProfile': staffProfile}
    return render(request, "staff_home.html", context)


@login_required(login_url='user_login')
def admin_zenotiCenter_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    usertype = staffProfile.user_type
    all_center = ZenotiCentersData.objects.all()
    all_center_list = []
    for each_center in all_center:
        extended_center_data = ExtendedZenotiCenterData.objects.get(
            zenoti_data=each_center)
        this_center_manager = ExtendedZenotiEmployeesData.objects.filter(
            associated_center=extended_center_data, is_manager=True)
        temp = {
            'id': each_center.id,
            'code': each_center.code,
            'name': each_center.name,
            'display_name': each_center.display_name,
            'address': f"{each_center.address_1 or ''}, {each_center.address_2 or ''}, "
            f"{each_center.zip_code or ''}, {each_center.city or ''}, "
            f"{each_center.state or ''}, {each_center.country or ''}",
            'manager': ', '.join(manager.zenoti_data.employee_name for manager in this_center_manager),
        }
        # print(temp)
        all_center_list.append(temp)

    if request.method == "POST":
        url = 'https://api.zenoti.com/v1/centers'
        head = {"Authorization": "apikey "+api_key}
        response = requests.request("GET", url, headers=head)
        response_got = json.loads(response.text)
        # print('response', response_got)
        for center in response_got['centers']:
            # print('each response', center['id'])
            try:
                existing_center = ZenotiCentersData.objects.get(
                    zenoticenterId=center['id'])
            except Exception:
                existing_center = None

            if existing_center is None:
                new_center = ZenotiCentersData.objects.create(
                    zenoticenterId=center['id'],
                    code=center['code'],
                    name=center['name'],
                    display_name=center['display_name'],
                    address_1=center['address_info']['address_1'],
                    address_2=center['address_info']['address_2'],
                    city=center['address_info']['city'],
                    zip_code=center['address_info']['zip_code'],
                    state=center['state']['name'],
                    country=center['country']['name'],
                )
                ExtendedZenotiCenterData.objects.create(
                    zenoti_data=new_center,
                    opening_time='09:00:00',
                    closing_time='22:00:00'
                )
        return redirect('zenotiCenter_page')
    context = {'all_center': all_center_list, 'staffProfile': staffProfile}
    return render(request, "admin_zenotiCentre.html", context)


@login_required(login_url='user_login')
def zenotiUsers_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    try:
        selected_center = request.GET.get('select_center')
    except Exception:
        selected_center = None
    try:
        selected_jobtitle = request.GET.get('select_jobtitle')
    except Exception:
        selected_jobtitle = None
    try:
        searched_text = request.GET.get('searched_text')
    except Exception:
        searched_text = None
    select_is_manager = request.GET.get('select_is_manager')
    # print('query', selected_center, selected_jobtitle, searched_text)
    try:
        searched_center = ZenotiCentersData.objects.get(
            id=int(selected_center))
    except Exception:
        searched_center = None
    try:
        searched_center_extend = ExtendedZenotiCenterData.objects.get(
            zenoti_data=searched_center)
    except Exception:
        searched_center_extend = None
    all_employee_query = ZenotiEmployeesData.objects.all().select_related(
        'user__user').prefetch_related('zenoti_center')
    all_employees = all_employee_query
    all_employees_extend_query = ExtendedZenotiEmployeesData.objects.all(
    ).select_related('zenoti_data').prefetch_related('associated_center__zenoti_data')
    all_employees_extend = all_employees_extend_query
    if searched_center:
        all_employees_extend = all_employees_extend.filter(
            associated_center=searched_center_extend)
        all_employees = all_employees.filter(
            id__in=all_employees_extend.values('zenoti_data')
        )
    if selected_jobtitle:
        all_employees = all_employees.filter(job_info=selected_jobtitle)
        all_employees_extend = all_employees_extend.filter(
            zenoti_data__in=all_employees
        )
    if select_is_manager:
        all_employees_extend = all_employees_extend.filter(
            is_manager=True)
        all_employees = all_employees.filter(
            id__in=all_employees_extend.values('zenoti_data')
        )

    if searched_text:
        split_text = searched_text.split()
        for text in split_text:
            all_employees = all_employees.filter(
                Q(employee_code__icontains=text) |
                Q(employee_name__icontains=text)
            )
            all_employees_extend = all_employees_extend.filter(
                zenoti_data__in=all_employees
            )
    employee_list = []
    for each_emp in all_employees:
        temp = {}
        temp['employee_code'] = each_emp.employee_code
        temp['name'] = each_emp.employee_name
        temp['username'] = each_emp.user.user.username
        temp['job'] = each_emp.job_info
        temp['gender'] = each_emp.gender
        temp['id'] = each_emp.id
        temp['assigned_center'] = ''
        for each_ex_emp in all_employees_extend:
            if each_emp == each_ex_emp.zenoti_data:
                for each_cent in each_ex_emp.associated_center.all():
                    temp['assigned_center'] += each_cent.zenoti_data.name+', '
        employee_list.append(temp)
    page = Paginator(employee_list, 20)
    page_num = request.GET.get('page', 1)
    try:
        staff_page = page.page(page_num)
    except EmptyPage:
        staff_page = page.page(1)
    all_centers = ZenotiCentersData.objects.all()
    all_jobtitle = ZenotiEmployeesData.objects.order_by(
    ).values_list('job_info', flat=True).distinct()
    # print('5', datetime.now())
    # print('jobtitle', all_jobtitle)
    if request.method == "POST":
        # print('start', datetime.now())
        for each_center in all_centers:
            page_number = 1
            while True:
                retry_count = 1
                c_id = each_center.zenoticenterId
                url = f"https://api.zenoti.com/v1/centers/{c_id}/employees?page={page_number}&size=100"
                head = {"Authorization": "apikey "+api_key}
                while True:
                    try:
                        response = requests.request("GET", url, headers=head)
                        break
                    except Exception:
                        time.sleep(5)
                        retry_count = retry_count+1
                        if retry_count > 5:
                            break
                response_got = json.loads(response.text)
                employees_got = response_got.get('employees')
                print(response_got)
                if not employees_got:
                    break
                for employee in employees_got:
                    try:
                        existing_employee_user = User.objects.get(
                            username=employee['personal_info']['user_name'])
                    except Exception:
                        existing_employee_user = None

                    if existing_employee_user is None:
                        new_user = User.objects.create_user(
                            username=employee['personal_info']['user_name'],
                            password=employee['id'],
                            first_name=employee['personal_info']['first_name'],
                            last_name=employee['personal_info']['last_name']
                        )
                        new_userprofile = UserProfile.objects.create(
                            user=new_user,
                            password=employee['id'],
                            user_type='Zenoti'
                        )
                        zenoti_employe_data = ZenotiEmployeesData.objects.create(
                            user=new_userprofile,
                            employee_code=employee['code'],
                            employee_id=employee['id'],
                            employee_name=employee['personal_info']['name'],
                            gender=employee['personal_info']['gender'],
                            job_info=employee['job_info']['name'],
                        )
                        zenoti_employe_data.zenoti_center.add(each_center)
                        ExtendedZenotiEmployeesData.objects.create(
                            zenoti_data=zenoti_employe_data,
                            office_start_time='09:00:00',
                            office_end_time='21:00:00'
                        )
                    else:
                        try:
                            existing_employee = ZenotiEmployeesData.objects.get(
                                employee_id=employee['id'])
                        except Exception:
                            existing_employee = None

                        if existing_employee:
                            existing_employee.employee_code = employee['code']
                            existing_employee.employee_name = employee['personal_info']['name']
                            existing_employee.gender = employee['personal_info']['gender']
                            existing_employee.job_info = employee['job_info']['name']
                            existing_employee.save()
                            if not each_center in existing_employee.zenoti_center.all():
                                existing_employee.zenoti_center.add(
                                    each_center)
                page_number = page_number+1
        print('end', datetime.now())
        return redirect('zenoti_staffs_list')
    context = {
        'staffProfile': staffProfile,
        'employee_list': staff_page,
        'all_centers': all_centers, 'all_jobtitle': all_jobtitle,
        'selected_center': selected_center,
        'selected_jobtitle': selected_jobtitle,
        'searched_text': searched_text,
        'select_is_manager': select_is_manager}
    return render(request, "zenotiUser.html", context)


@login_required(login_url='user_login')
def admin_employee_profile_page(request, pk):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    usertype = staffProfile.user_type
    employee_detail = ZenotiEmployeesData.objects.get(id=pk)
    try:
        extra_employee_detail = ExtendedZenotiEmployeesData.objects.get(
            zenoti_data=employee_detail)
    except Exception:
        extra_employee_detail = None

    try:
        employee_leave_detail = ExtendedZenotiEmployeesLeaveData.objects.filter(
            zenoti_data=extra_employee_detail)
    except Exception:
        employee_leave_detail = None
    form = ExtendedZenotiDataForm(
        request.POST or None, instance=extra_employee_detail)
    is_roster = employee_detail.user.roster_access
    all_centers = ZenotiCentersData.objects.all()
    all_roles = AssociatedRoleOptions.objects.all()
    all_weekoff = WeekOffOptions.objects.all()
    if request.method == 'POST':
        if 'extra_data_form' in request.POST:
            if form.is_valid():
                is_roster_access = request.POST.get('is_roster_check') == 'on'
                this_userprofile = employee_detail.user
                this_userprofile.roster_access = is_roster_access
                this_userprofile.save()
                form.save()
        if 'set_staff_password' in request.POST:
            new_pass = request.POST.get('new_password')
            user_of_this_profile = employee_detail.user.user
            user_of_this_profile.set_password(new_pass)
            user_of_this_profile.save()
            extra_employee_detail.password = new_pass
            extra_employee_detail.save()

        if 'leave_form' in request.POST:
            leave_from = request.POST.get('leave_from')
            leave_to = request.POST.get('leave_to')
            leave_note = request.POST.get('leave_note')
            leave_status = request.POST.get('leave_status')

            ExtendedZenotiEmployeesLeaveData.objects.create(
                zenoti_data=extra_employee_detail,
                leave_from_date=leave_from,
                leave_to_date=leave_to,
                note=leave_note,
                status=leave_status
            )

        if 'leave_form_edit' in request.POST:
            leave_id = request.POST.get('edit_leave_id')
            leave_from = request.POST.get('edit_leave_from')
            leave_to = request.POST.get('edit_leave_to')
            leave_note = request.POST.get('edit_leave_note')
            leave_status = request.POST.get('edit_leave_status')
            try:
                leave_query = ExtendedZenotiEmployeesLeaveData.objects.get(
                    id=int(leave_id))
            except Exception:
                leave_query = None
            leave_query.leave_from_date = leave_from
            leave_query.leave_to_date = leave_to
            leave_query.note = leave_note
            leave_query.status = leave_status
            leave_query.save()
        if 'remove_center' in request.POST:
            today_date = date.today()
            center_id = request.POST.get('remove_centers')
            try:
                center = ExtendedZenotiCenterData.objects.get(
                    id=int(center_id))
            except Exception:
                center = None

            all_schedulers = EmployeeScheduler.objects.filter(
                employee=extra_employee_detail, center=center)

            all_rosters = EmployeeRoster.objects.filter(
                employee=extra_employee_detail, center=center
            )
            print(today_date)
            extra_employee_detail.associated_center.remove(center)
            for scheduler in all_schedulers:
                if scheduler.appoint_date >= today_date:
                    scheduler.delete()

            for roster in all_rosters:
                if roster.appoint_date >= today_date:
                    roster.delete()

        return redirect('body_craft_staff_profile', pk=pk)

    context = {'staffProfile': staffProfile,
               'extra_employee_detail': extra_employee_detail,
               'employee_detail': employee_detail, 'form': form,
               'all_weekoff': all_weekoff, 'all_roles': all_roles,
               'all_centers': all_centers,
               'employee_leave_detail': employee_leave_detail,
               'is_roster': is_roster}
    return render(request, "admin_employee_profile.html", context)


@login_required(login_url='user_login')
def admin_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    usertype = staffProfile.user_type
    is_slr_salon_auditor = SLRSalonAuditAccess.objects.filter(
        auditors=staffProfile).exists()
    print(is_slr_salon_auditor)
    all_centers = ZenotiCentersData.objects.all()
    total_center = all_centers.count()
    all_employees = UserProfile.objects.all()
    total_employees = all_employees.count()
    context = {'is_slr_salon_auditor': is_slr_salon_auditor,
               'total_center': total_center,
               'total_employees': total_employees,
               'staffProfile': staffProfile}
    return render(request, "admin_home.html", context)


# @login_required(login_url='user_login')
# def add_admin(request):
#     user = request.user
#     staffProfile = UserProfile.objects.get(user=user)
#     all_user = UserProfile.objects.all().exclude(user__is_superuser=True)
#     if request.method == "POST":
#         phone = request.POST.get("phone")
#         passcode = request.POST.get("passcode")
#         name = request.POST.get("name")
#         username = request.POST.get("email")
#         try:
#             already_user = User.objects.get(username=username)
#         except Exception:
#             already_user = None
#             # print('user', already_user)
#         if already_user is None:
#             new_user = User.objects.create_user(
#                 username=username, password=passcode, first_name=name)
#             UserProfile.objects.create(
#                 user=new_user,
#                 phone=phone,
#                 email=username,
#                 password=passcode,
#                 user_type='admin',
#             )
#             return redirect('admin_team')
#         else:
#             messages.info(
#                 request, 'This Email Id is already exist in our DataBase')
#             return redirect('admin_team')
#     context = {'all_user': all_user, 'staffProfile': staffProfile}
#     return render(request, "admin_team.html", context)


@login_required(login_url='user_login')
def other_user_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    audit_user = UserProfile.objects.filter(
        user_type='Non Zenoti').exclude(user__is_superuser=True)
    if request.method == "POST":
        if 'new_audit_user' in request.POST:
            phone = request.POST.get("phone")
            passcode = request.POST.get("passcode")
            name = request.POST.get("name")
            username = request.POST.get("email")
            try:
                already_user = User.objects.get(username=username)
            except Exception:
                already_user = None
                # print('user', already_user)
            if already_user is None:
                new_user = User.objects.create_user(
                    username=username, password=passcode, first_name=name)
                UserProfile.objects.create(
                    user=new_user,
                    phone=phone,
                    email=username,
                    password=passcode,
                    user_type='Non Zenoti',
                    user_status='Active',
                )
            else:
                messages.info(
                    request, 'This Email Id is already exist in our DataBase')
        if 'edit_audit_user' in request.POST:
            user_id = request.POST.get('audit_user_id')
            name = request.POST.get('edit_name')
            phone = request.POST.get('edit_phone')
            email = request.POST.get('edit_email')
            user_status = request.POST.get('edit_user_status')
            try:
                audit_user = UserProfile.objects.get(id=int(user_id))
            except Exception:
                audit_user = None

            audit_user.phone = phone
            audit_user.email = email
            audit_user.user_status = user_status
            audit_user.save()

            main_user = audit_user.user
            main_user.first_name = name
            main_user.save()
        if 'update_user_password' in request.POST:
            user_id = request.POST.get("user_id")
            passcode = request.POST.get("edit_passcode")
            try:
                audit_user = UserProfile.objects.get(id=int(user_id))
            except Exception:
                audit_user = None
            audit_user.password = passcode
            audit_user.save()
            main_user = audit_user.user
            main_user.set_password(passcode)
            main_user.save()
        return redirect('other_staffs_list')
    context = {'audit_user': audit_user,
               'staffProfile': staffProfile}
    return render(request, "users_page.html", context)


def edit_user_modal_popup(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print("data", got_query)
        try:
            audit_user = UserProfile.objects.get(
                id=int(got_query))
        except Exception:
            audit_user = None
        user_json = serializers.serialize('json', [audit_user])
        return JsonResponse({"msg": "success",
                            "user_json": json.loads(user_json), 'user_name': audit_user.user.first_name})


@login_required(login_url='user_login')
def admin_team_list_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    all_user_list = UserProfile.objects.all().exclude(user__is_superuser=True)

    admin_team = UserProfile.objects.filter(
        Q(is_super_admin=True) | Q(is_audit_admin=True)).exclude(user__is_superuser=True)
    if request.method == "POST":
        if 'new_admin_assign' in request.POST:
            user_id = request.POST.get("admin_assign_to")
            user_type = request.POST.get("admin_type")
            try:
                already_user = UserProfile.objects.get(id=int(user_id))
            except UserProfile.DoesNotExist:
                already_user = None
            print(already_user)
            if already_user:
                already_user.is_super_admin = False
                already_user.is_audit_admin = False
                already_user.user_type_name.clear()
                if user_type == 'System Admin':
                    already_user.is_super_admin = True
                elif user_type == 'Audit Admin':
                    already_user.is_audit_admin = True
                already_user.save()
        return redirect('admin_team_list_page')
    context = {'admin_team': admin_team,
               'all_user_list': all_user_list,
               'staffProfile': staffProfile}
    return render(request, "admin_team_page.html", context)


def edit_admin_modal_popup(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        try:
            audit_user_query = UserProfile.objects.get(id=int(got_query))
        except UserProfile.DoesNotExist:
            audit_user_query = None
        audit_user_data = {}
        if audit_user_query:
            audit_user_data['id'] = audit_user_query.id
            audit_user_data['is_audit_admin'] = audit_user_query.is_audit_admin
            audit_user_data['is_super_admin'] = audit_user_query.is_super_admin

        # user_json = serializers.serialize('json', [audit_user_data])
        return JsonResponse({"msg": "success", "user_json": audit_user_data})


compliance_category_percentage = {
    "RNR": 100,
    "Benchmark KRA": 50,
    "CPI": 0,
    "PIP": 0,
    "Education": 0
}


def sanitize_name(name):
    return re.sub(r'[^a-zA-Z\s]', '', name)


def sent_selected_user_list_to_frontend(request):
    if request.method == "POST":
        data = json.loads(request.body)
        audit_name = data['audit_name']
        audit_id = data['audit_id']
        if audit_id:
            if audit_name == 'Mystery Shopping':
                audit_detail_query = MysteryShoppingDetail.objects.get(
                    id=int(audit_id))

            all_users = []
            for each_user in audit_detail_query.staff.all():
                all_users.append(each_user.id)
            return JsonResponse({"msg": "success", "user_json": all_users})
        else:
            return JsonResponse({"msg": "failed"})


def save_selected_user_responsible(request):
    if request.method == "POST":
        data = json.loads(request.body)
        audit_name = data['audit_name']
        audit_id = data['audit_id']
        audit_value = data['audit_value']
        # print(audit_value, audit_id, audit_name)
        user_query = None
        all_users = []
        if audit_id:
            if audit_name == 'Mystery Shopping':
                audit_detail_query = MysteryShoppingDetail.objects.get(
                    id=int(audit_id))
                try:
                    user_ids = [int(id) for id in audit_value]
                    user_query = UserProfile.objects.filter(id__in=user_ids)
                except Exception:
                    user_query = None
                # print('user_q', user_query)
                audit_detail_query.staff.set(user_query)
                audit_detail_query.save()
                # print('yes')
            for each_user in user_query:
                tempUserObj = {}
                tempUserObj["id"] = each_user.id
                sanitized_first_name = sanitize_name(each_user.user.first_name)
                sanitized_last_name = sanitize_name(each_user.user.last_name)
                tempUserObj["name"] = f"{sanitized_first_name} {sanitized_last_name}"
                all_users.append(tempUserObj)
        if audit_id:
            return JsonResponse({"msg": "success", "user_json": all_users})
        else:
            return JsonResponse({"msg": "failed"})


@login_required(login_url='user_login')
def central_access_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    all_users_query = UserProfile.objects.all().exclude(is_super_admin=True)
    all_users = []
    for each_user in all_users_query:
        tempUserObj = {}
        tempUserObj["id"] = each_user.id
        sanitized_first_name = sanitize_name(each_user.user.first_name)
        sanitized_last_name = sanitize_name(each_user.user.last_name)
        tempUserObj["name"] = f"{sanitized_first_name} {sanitized_last_name}"
        all_users.append(tempUserObj)
    all_center = ExtendedZenotiCenterData.objects.filter(
        center_status='Active')
    all_audit = AuditTypes.objects.all()
    all_access = CentralAccess.objects.all()
    if request.method == 'POST':
        if 'add_access_alotment' in request.POST:
            staff_id = request.POST.getlist('staff_select')
            audit_id = request.POST.getlist('audit_select')
            auditor_id = request.POST.getlist('auditor_select')
            project_owner_id = request.POST.getlist('project_owner_select')
            reviewer_id = request.POST.getlist('reviewer_select')
            senior_management_id = request.POST.getlist(
                'senior_management_select')
            try:
                staff_query = UserProfile.objects.filter(id__in=staff_id)
            except Exception:
                staff_query = None
            try:
                audit_query = AuditTypes.objects.filter(id__in=audit_id)
            except Exception:
                audit_query = None
            try:
                auditor_query = ExtendedZenotiCenterData.objects.filter(
                    id__in=auditor_id)
            except Exception:
                auditor_query = None
            try:
                project_owner_query = ExtendedZenotiCenterData.objects.filter(
                    id__in=project_owner_id)
            except Exception:
                project_owner_query = None
            try:
                reviewer_query = ExtendedZenotiCenterData.objects.filter(
                    id__in=reviewer_id)
            except Exception:
                reviewer_query = None
            try:
                senior_management_query = ExtendedZenotiCenterData.objects.filter(
                    id__in=senior_management_id)
            except Exception:
                senior_management_query = None

            new_access = CentralAccess.objects.create()
            new_access.staff.set(staff_query)
            new_access.audit.set(audit_query)
            new_access.auditor.set(auditor_query)
            new_access.project_owner.set(project_owner_query)
            new_access.audit_reviewer.set(reviewer_query)
            new_access.senior_management.set(senior_management_query)
            new_access.save()
        if 'del_user_access' in request.POST:
            access_id = request.POST.get('del_id')
            try:
                access_query = CentralAccess.objects.get(id=int(access_id))
            except Exception:
                access_query = None
            if access_query:
                access_query.delete()
        if 'edit_access_alotment' in request.POST:
            access_id = request.POST.get('audit_access_id')
            staff_id = request.POST.getlist('edit_staff_select')
            audit_id = request.POST.getlist('edit_audit_select')
            auditor_id = request.POST.getlist('edit_auditor_select')
            project_owner_id = request.POST.getlist(
                'edit_project_owner_select')
            reviewer_id = request.POST.getlist('edit_reviewer_select')
            senior_management_id = request.POST.getlist(
                'edit_senior_management_select')
            try:
                access_query = CentralAccess.objects.get(id=int(access_id))
            except Exception:
                access_query = None
            try:
                staff_query = UserProfile.objects.filter(id__in=staff_id)
            except Exception:
                staff_query = None
            try:
                audit_query = AuditTypes.objects.filter(id__in=audit_id)
            except Exception:
                audit_query = None
            try:
                auditor_query = ExtendedZenotiCenterData.objects.filter(
                    id__in=auditor_id)
            except Exception:
                auditor_query = None
            try:
                project_owner_query = ExtendedZenotiCenterData.objects.filter(
                    id__in=project_owner_id)
            except Exception:
                project_owner_query = None
            try:
                reviewer_query = ExtendedZenotiCenterData.objects.filter(
                    id__in=reviewer_id)
            except Exception:
                reviewer_query = None
            try:
                senior_management_query = ExtendedZenotiCenterData.objects.filter(
                    id__in=senior_management_id)
            except Exception:
                senior_management_query = None

            access_query.staff.set(staff_query)
            access_query.audit.set(audit_query)
            access_query.auditor.set(auditor_query)
            access_query.project_owner.set(project_owner_query)
            access_query.audit_reviewer.set(reviewer_query)
            access_query.senior_management.set(senior_management_query)
            access_query.save()
        return redirect('central_audit_access')
    context = {'staffProfile': staffProfile,
               'all_center': all_center,
               'all_audit': all_audit,
               'all_users': all_users,
               'all_access': all_access}
    return render(request, "central_access_page.html", context)


def edit_central_access_popup(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print("data", got_query)
        try:
            access_query = CentralAccess.objects.get(
                id=int(got_query))
        except Exception:
            access_query = None
        access_query_json = serializers.serialize('json', [access_query])
        print(access_query_json)
        return JsonResponse({"msg": "success",
                            "access_json": json.loads(access_query_json)})


@login_required(login_url='user_login')
def slr_audit_access(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    try:
        # slr_auditors, created = SLRSalonAuditAccess.objects.get_or_create()
        slr_auditors = SLRSalonAuditAccess.objects.first()
    except Exception:
        slr_auditors = None

    if slr_auditors is None:
        SLRSalonAuditAccess.objects.create()

    all_users = UserProfile.objects.all().exclude(is_super_admin=True)
    all_slr_access_list = AuditAccess.objects.filter(audit='SLR Salon')
    try:
        all_audit_users = slr_auditors.auditors.all()
    except Exception:
        all_audit_users = None
    all_center = ExtendedZenotiCenterData.objects.filter(
        center_status='Active')
    all_user_type = UserTypes.objects.exclude(
        user_type__in=['Audit Admin', 'Auditor']).all()
    if request.method == 'POST':
        if 'add_auditors' in request.POST:
            auditors_id = request.POST.getlist('auditor_access_select')
            try:
                selected_auditors = UserProfile.objects.filter(
                    id__in=auditors_id)
                slr_auditors.auditors.set(selected_auditors)
                slr_auditors.save()
            except Exception:
                pass
        if 'add_auditor_access_alotment' in request.POST:
            center_id = request.POST.get('add_center')
            user_type_id = request.POST.get('add_user_type')
            view_user_id = request.POST.getlist(
                'add_auditor_view_access_select')
            edit_user_id = request.POST.getlist(
                'add_auditor_edit_access_select')
            try:
                center = ExtendedZenotiCenterData.objects.get(
                    id=int(center_id))
            except Exception:
                center = None

            try:
                user_type = UserTypes.objects.get(id=int(user_type_id))
            except Exception:
                user_type = None

            try:
                view_users = UserProfile.objects.filter(id__in=view_user_id)
            except Exception:
                view_users = None

            try:
                edit_users = UserProfile.objects.filter(id__in=edit_user_id)
            except Exception:
                edit_users = None
            new_audit_access = AuditAccess.objects.create(
                audit='SLR Salon',
                center=center,
                user_type_name=user_type,
            )
            new_audit_access.view_access.set(view_users)
            new_audit_access.edit_access.set(edit_users)
            new_audit_access.save()
        if 'edit_auditor_access_alotment' in request.POST:
            got_access_id = request.POST.get('audit_access_id')
            center_id = request.POST.get('edit_center')
            user_type_id = request.POST.get('edit_user_type')
            view_user_id = request.POST.getlist(
                'edit_auditor_view_access_select')
            edit_user_id = request.POST.getlist(
                'edit_auditor_edit_access_select')
            try:
                center = ExtendedZenotiCenterData.objects.get(
                    id=int(center_id))
            except Exception:
                center = None

            try:
                user_type = UserTypes.objects.get(id=int(user_type_id))
            except Exception:
                user_type = None

            try:
                view_users = UserProfile.objects.filter(id__in=view_user_id)
            except Exception:
                view_users = None

            try:
                edit_users = UserProfile.objects.filter(id__in=edit_user_id)
            except Exception:
                edit_users = None
            audit_access_query = AuditAccess.objects.get(id=int(got_access_id))
            audit_access_query.center = center
            audit_access_query.user_type_name = user_type
            audit_access_query.view_access.set(view_users)
            audit_access_query.edit_access.set(edit_users)
            audit_access_query.save()

        return redirect('slr_audit_access')
    context = {'staffProfile': staffProfile,
               'all_center': all_center,
               'all_users': all_users,
               'all_slr_access_list': all_slr_access_list,
               'all_audit_users': all_audit_users,
               'all_audit_users': all_audit_users,
               'all_user_type': all_user_type, }
    return render(request, "slr_salon/slr_access_page.html", context)


def edit_slr_access_popup(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print("data", got_query)
        try:
            access_query = AuditAccess.objects.get(
                id=int(got_query))
        except Exception:
            access_query = None
        access_query_json = serializers.serialize('json', [access_query])
        return JsonResponse({"msg": "success",
                            "access_json": json.loads(access_query_json)})


@login_required(login_url='user_login')
def slr_audit_overview(request):
    current_time = datetime.now().time()
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    is_slr_salon_auditor = SLRSalonAuditAccess.objects.filter(
        auditors=staffProfile).exists()
    all_center = ExtendedZenotiCenterData.objects.filter(
        center_status='Active')
    try:
        slr_auditors = SLRSalonAuditAccess.objects.first().auditors.all()
    except Exception:
        slr_auditors = None
    all_slr_audit = SlrAudit.objects.filter(
        is_deleted=False).order_by('-id')
    all_months = MonthAudit.objects.all()
    all_slr_detail = SlrDetail.objects.filter(slr_audit__in=all_slr_audit, audit_status__in=[
                                              'Completed', 'Action Required', 'Action Taken'])
    all_slr_salon_image = SlrSalonImages.objects.all()
    all_ext_emp = ExtendedZenotiEmployeesData.objects.all().select_related('zenoti_data')
    all_therapy_ext_emp = []
    for each_employee in all_ext_emp:
        temp = {}
        temp['id'] = each_employee.id
        temp['name'] = each_employee.zenoti_data.employee_name
        all_therapy_ext_emp.append(temp)
    slr_form = SlrAuditForm(request.POST or None)
    slr_form.fields['access_given_to'].queryset = slr_auditors
    selected_center_ids = request.GET.getlist('select_center')
    searched_from_id = request.GET.get('searched_from_id')
    select_audit_status = request.GET.get('select_audit_status')
    searched_month = request.GET.get('select_month')
    searched_text = request.GET.get('searched_text')
    searched_compliance = request.GET.getlist('searched_compliance')
    searched_kra = request.GET.get('searched_kra')
    searched_dept = request.GET.get('searched_dept')
    searched_om = request.GET.get('searched_om')
    unique_kra_fieled = SlrDetail.objects.order_by(
    ).values_list('kra_responsible', flat=True).distinct()
    try:
        selected_center = ExtendedZenotiCenterData.objects.filter(
            id__in=selected_center_ids)
    except Exception:
        selected_center = None

    try:
        selected_month = MonthAudit.objects.get(id=int(searched_month))
    except Exception:
        selected_month = None

    if selected_center:
        all_slr_audit = all_slr_audit.filter(center__in=selected_center)
        all_slr_detail = all_slr_detail.filter(
            center__in=selected_center)
        all_slr_salon_image = all_slr_salon_image.filter(
            center__in=selected_center
        )
    if searched_from_id:
        all_slr_audit = all_slr_audit.filter(id=int(searched_from_id))
        all_slr_detail = all_slr_detail.filter(
            slr_audit__in=all_slr_audit)
        all_slr_salon_image = all_slr_salon_image.filter(
            slr_audit__in=all_slr_audit
        )
    if select_audit_status:
        if select_audit_status == 'All':
            all_slr_detail = SlrDetail.objects.filter(slr_audit__in=all_slr_audit,
                                                      audit_status__in=['Completed',
                                                                        'Action Required', 'Action Taken', 'Pending']
                                                      )
        elif select_audit_status == 'Pending':
            all_slr_detail = SlrDetail.objects.filter(slr_audit__in=all_slr_audit,
                                                      audit_status=select_audit_status)
        else:
            all_slr_detail = all_slr_detail.filter(
                audit_status=select_audit_status)

    if selected_month:
        all_slr_audit = all_slr_audit.filter(
            month_of_audit=selected_month)
        all_slr_detail = all_slr_detail.filter(
            slr_audit__in=all_slr_audit)
        all_slr_salon_image = all_slr_salon_image.filter(
            slr_audit__in=all_slr_audit
        )

    if searched_compliance:
        all_slr_detail = all_slr_detail.filter(
            compliance_category__in=searched_compliance)

    if searched_kra:
        all_slr_detail = all_slr_detail.filter(kra_responsible=searched_kra)

    if searched_om:
        all_slr_detail = all_slr_detail.filter(
            status_by_om=searched_om
        )
    if searched_dept:
        all_slr_detail = all_slr_detail .filter(
            status_by_department=searched_dept
        )
    if is_slr_salon_auditor:
        all_slr_audit = all_slr_audit.filter(
            Q(access_given_to__in=staffProfile) | Q(added_by=staffProfile))
        all_slr_detail = all_slr_detail.filter(
            slr_audit__in=all_slr_audit)
        all_slr_salon_image = all_slr_salon_image.filter(
            slr_audit__in=all_slr_audit
        )

    slr_overview_query = []
    for overview in all_slr_audit:
        all_not_blank_question = SlrDetail.objects.filter(
            slr_audit=overview).exclude(audit_status='')
        total_completed = all_not_blank_question.filter(
            audit_status='Completed')
        total_pending = all_not_blank_question.filter(audit_status='Pending')
        total_action_required = all_not_blank_question.filter(
            audit_status='Action Required')
        total_action_taken = all_not_blank_question.filter(
            audit_status='Action Taken')
        not_rnr = all_not_blank_question.filter(
            Q(compliance_category_percentage='0') | Q(compliance_category_percentage='50'))
        om_actioned = not_rnr.filter(action_taken_by_outlet_manager__isnull=False,
                                     status_by_om__isnull=False, remark_by_om__isnull=False).exclude(action_taken_by_outlet_manager='').exclude(status_by_om='').exclude(remark_by_om='')
        try:
            month_audit = overview.month_of_audit.month
        except Exception:
            month_audit = None
        temp = {}
        temp['id'] = overview.id
        # temp['added_by'] = overview.added_by.user.first_name
        temp['added_on'] = overview.added_on
        temp['auditor_name'] = overview.auditor_name
        temp['month_audit'] = month_audit
        temp['date'] = overview.date_of_audit
        temp['center'] = overview.center.zenoti_data.name
        temp['center_id'] = overview.center.id
        temp['total_question'] = all_not_blank_question.count()
        temp['total_completed_question'] = total_completed.count()
        temp['total_pending_question'] = total_pending.count()
        temp['total_action_required_question'] = total_action_required.count()
        temp['total_action_taken_question'] = total_action_taken.count()
        temp['not_rnr'] = not_rnr.count()
        temp['om_actioned'] = om_actioned.count()
        temp['auditor_action_reviewed'] = overview.auditor_action_reviewed
        temp['om_action_reviewed'] = overview.om_action_reviewed
        slr_overview_query.append(temp)
    # list pagination
    page = Paginator(slr_overview_query, 20)
    list_page_num = request.GET.get('page', 1)
    try:
        list_page = page.page(list_page_num)
    except EmptyPage:
        list_page = page.page(1)

    list_start_index = (int(list_page_num) - 1) * page.per_page + 1
    list_end_index = min(list_start_index + page.per_page - 1, page.count)
    print('11', current_time)
    # detail pagination
    page_2 = Paginator(all_slr_detail, 50)
    detail_page_num = request.GET.get('page_2', 1)
    try:
        detail_page = page_2.page(detail_page_num)
    except EmptyPage:
        detail_page = page_2.page(1)
    detail_start_index = (int(detail_page_num) - 1) * page_2.per_page + 1
    detail_end_index = min(detail_start_index +
                           page_2.per_page - 1, page_2.count)

    page_3 = Paginator(all_slr_salon_image, 20)
    image_page_num = request.GET.get('page_3', 1)
    try:
        image_page = page_3.page(image_page_num)
    except EmptyPage:
        image_page = page_3.page(1)
    if request.method == 'POST':
        data_json = open("slr_salon_checklist.txt", "r")
        slr_detail_data = json.loads(data_json.read())
        if 'slr_audit_form' in request.POST:
            if slr_form.is_valid():
                new_slr_audit = slr_form.save(commit=False)
                new_slr_audit.added_by = staffProfile
                new_slr_audit.save()
                # ***if a form is having manytomany field and while saving the form there is commit=False in use then to save the manytomany field you have to do the below line
                slr_form.save_m2m()
                for overview in slr_detail_data:
                    # print(type(overview['service_number']))
                    SlrDetail.objects.create(
                        slr_audit=new_slr_audit,
                        center=new_slr_audit.center,
                        month_of_audit=new_slr_audit.month_of_audit,
                        date=new_slr_audit.date_of_audit,
                        sequence=overview['Sequence'],
                        audited_by=overview['Audited By'],
                        kra_responsible=overview['KRA Responsible'],
                        protocol=overview['Protocol'],
                        checklist=overview['Checklist'],
                        methodology=overview['Methodology'],
                        compliance_dropdown=overview['dropdown'],
                        audit_status='Pending'
                    )
        if 'del_slr_salon' in request.POST:
            del_audit_id = request.POST.get('del_id')
            try:
                slr_audit = SlrAudit.objects.get(
                    id=int(del_audit_id))
            except Exception:
                slr_audit = None

            slr_audit.is_deleted = True
            slr_audit.save()
        if 'edit_slr_salon' in request.POST:
            slr_salon_pk = request.POST.get('slr_salon_pk')
            center_id = request.POST.get('edit_center')
            auditor_name = request.POST.get('edit_auditor_name')
            trainer_name = request.POST.get('edit_trainer_name')
            month_id = request.POST.get('edit_month')
            date = request.POST.get('edit_date')
            access_auditor_id = request.POST.getlist(
                'edit_auditor_access_select')

            try:
                slr_audit = SlrAudit.objects.get(
                    id=int(slr_salon_pk))
            except Exception:
                slr_audit = None

            try:
                center = ExtendedZenotiCenterData.objects.get(
                    id=int(center_id))
            except Exception:
                center = None

            try:
                slr_detail = SlrDetail.objects.filter(
                    slr_audit=slr_audit)
            except Exception:
                slr_detail = None

            try:
                slr_files = SlrSalonImages.objects.filter(
                    slr_audit=slr_audit
                )
            except Exception:
                slr_files = None

            try:
                month_query = MonthAudit.objects.get(id=int(month_id))
            except Exception:
                month_query = None

            try:
                auditors = UserProfile.objects.filter(id__in=access_auditor_id)
            except Exception:
                auditors = None

            slr_audit.center = center
            slr_audit.auditor_name = auditor_name
            slr_audit.trainer_name = trainer_name
            slr_audit.month_of_audit = month_query
            slr_audit.date_of_audit = date
            slr_audit.access_given_to.set(auditors)
            slr_audit.save()

            for each_detail in slr_detail:
                each_detail.center = center
                each_detail.date = date
                each_detail.month_of_audit = month_query
                each_detail.save()

            for each_file in slr_files:
                each_file.center = center
                each_file.save()

        if 'slr_salon_atr_csv' in request.POST:
            csv_headers = [
                'SLR ID', 'Checklist ID', 'Center', 'Month of Audit', 'audited_by', 'KRA', 'Protocol', 'Checklist', 'Compliance', 'Compliance Category', 'Compliance Category Percentage', 'Methodology', 'User Responsible', 'Remark By Auditor', 'Action Taken By Outlet Manager', 'Status By Om', 'Remark By OM', 'Action Taken By Management', 'Remark By Management', 'Expected Dept/Personnel to Intervene', 'Remark By Department', 'Status By Department'
            ]
            rows = []

            for each_detail in all_slr_detail:
                try:
                    user_responsible = each_detail.person_responsible.zenoti_data.employee_name
                except Exception:
                    user_responsible = ''

                try:
                    month_audit = each_detail.slr_audit.month_of_audit.month
                except Exception:
                    month_audit = ''
                rows.append([
                    each_detail.slr_audit.id,
                    each_detail.id,
                    each_detail.center.zenoti_data.name,
                    month_audit,
                    each_detail.audited_by,
                    each_detail.kra_responsible,
                    each_detail.protocol,
                    each_detail.checklist,
                    each_detail.compliance,
                    each_detail.compliance_category,
                    each_detail.compliance_category_percentage,
                    each_detail.methodology,
                    user_responsible,
                    each_detail.audit_remarks,
                    each_detail.action_taken_by_outlet_manager,
                    each_detail.status_by_om,
                    each_detail.remark_by_om,
                    each_detail.action_taken_by_management,
                    each_detail.remark_by_management,
                    each_detail.expected_dept_intervene,
                    each_detail.remark_by_department,
                    each_detail.status_by_department
                ])
            csv_response = HttpResponse(content_type='text/csv')
            csv_response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
                'slr_salon_atr-' + str(datetime.today().date()) + '.csv')
            writer = csv.writer(csv_response)
            writer.writerow(csv_headers)
            writer.writerows(rows)
            return csv_response
        if 'slr_list_csv' in request.POST:
            csv_headers = [
                'ID', 'Added By', 'Center', 'Auditor Name', 'Trainer Name', 'Month of Audit', 'Date'
            ]
            rows = []
            for each_list in all_slr_audit:
                try:
                    added_by = each_list.added_by.user.first_name
                except Exception:
                    added_by = ''
                try:
                    month_audit = each_list.month_of_audit.month
                except Exception:
                    month_audit = ''

                rows.append([
                    each_list.id,
                    added_by,
                    each_list.center.zenoti_data.name,
                    each_list.auditor_name,
                    each_list.trainer_name,
                    month_audit,
                    each_list.date_of_audit,
                ])
            csv_response = HttpResponse(content_type='text/csv')

            csv_response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
                'slr_salon_list-' + str(datetime.today().date()) + '.csv')
            writer = csv.writer(csv_response)
            writer.writerow(csv_headers)
            writer.writerows(rows)
            # print('response', csv_response)
            return csv_response

        return redirect('slr_salon')
    context = {'all_slr_list': list_page,
               'staffProfile': staffProfile,
               'slr_form': slr_form,
               'all_center': all_center,
               'slr_auditors': slr_auditors,
               'all_slr_atr': detail_page,
               'is_slr_salon_auditor': is_slr_salon_auditor,
               #    'slr_overview_query': slr_overview_query,
               'all_slr_salon_image': image_page,
               #    'all_employee': all_employee,
               'selected_center_id': selected_center_ids,
               'list_start_index': list_start_index,
               'list_end_index': list_end_index,
               'list_total': page.count,
               'detail_start_index': detail_start_index,
               'detail_end_index': detail_end_index,
               'detail_total': page_2.count,
               #    'searched_from_date': searched_from_date,
               #    'searched_to_date': searched_to_date,
               'select_audit_status': select_audit_status,
               'searched_month': searched_month,
               'searched_text': searched_text,
               'searched_from_id': searched_from_id,
               'searched_compliance': searched_compliance,
               'unique_kra_filed': unique_kra_fieled,
               #    'unique_process_fieled': unique_process_fieled,
               'searched_kra': searched_kra,
               'searched_dept': searched_dept,
               'searched_om': searched_om,
               'all_months': all_months,
               #    'compliance_category_percentage': compliance_category_percentage,
               'all_therapy_ext_emp': all_therapy_ext_emp}
    return render(request, "slr_salon/slr_overview_tab.html", context)


@login_required(login_url='user_login')
def slr_audit_detail(request, pk):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    is_slr_salon_auditor = SLRSalonAuditAccess.objects.filter(
        auditors=staffProfile).exists()
    try:
        slr_audit = SlrAudit.objects.get(id=int(pk))
    except Exception:
        slr_audit = None
    all_employee = ExtendedZenotiEmployeesData.objects.filter(
        associated_center=slr_audit.center)
    all_slr_detail = SlrDetail.objects.filter(slr_audit=slr_audit)
    all_images_list = SlrSalonImages.objects.filter(slr_audit=slr_audit)
    # all_therapy_ext_emp = ExtendedZenotiEmployeesData.objects.all()
    if request.method == 'POST':
        if 'image_submit' in request.POST:
            description = request.POST.get('desc')
            image = request.FILES["selected_img"]
            SlrSalonImages.objects.create(
                slr_audit=slr_audit,
                center=slr_audit.center,
                date=slr_audit.date_of_audit,
                description=description,
                image=image
            )
        if 'image_delete' in request.POST:
            img_id = request.POST.get('img_id')
            try:
                slr_image = SlrSalonImages.objects.get(
                    id=int(img_id))
            except Exception:
                slr_image = None
            slr_image.delete()
        return redirect('slr_salon_profile', pk=pk)

    context = {'is_slr_salon_auditor': is_slr_salon_auditor,
               'all_slr_detail': all_slr_detail,
               'slr_audit': slr_audit,
               'all_images_list': all_images_list,
               'staffProfile': staffProfile,
               'all_employee': all_employee,
               'total_length': all_slr_detail.count(),
               }
    return render(request, "slr_salon/slr_profile_tab.html", context)


def edit_slr_audit(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print("data", got_query)
        try:
            slr_audit = SlrAudit.objects.get(
                id=int(got_query))
        except Exception:
            slr_audit = None

        slr_json = serializers.serialize('json', [slr_audit])
        return JsonResponse({"msg": "success",
                            "slr_json": json.loads(slr_json)})
    return render(request, "slr_salon/slr_overview_tab.html")


def edit_slr_salon_profile(request):
    compliance_category_value = {
        "Followed": "RNR",
        "Partially followed": "Benchmark KRA",
        "Couldn't follow": "CPI",
        "Not aware": "Education",
        "Not followed": "PIP",
        "1": "PIP",
        "2": "PIP",
        "3": "PIP",
        "4": "Benchmark KRA",
        "5": "RNR",
        "Like": "RNR",
        "Partially Like": "Benchmark KRA",
        "Dislike": "PIP",
        "Yes": "RNR",
        "No": "PIP",
        "May be": "Benchmark KRA",
        "NA": "NA"
    }
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        print('get_query', got_query)
        if got_query:
            for query in got_query:
                slr_detail = SlrDetail.objects.get(
                    id=int(query['id']))
                try:
                    employee = ExtendedZenotiEmployeesData.objects.get(
                        id=int(query['staff']))
                except Exception:
                    employee = None
                compliance_value = query['compliance']
                slr_detail.compliance = query['compliance']
                slr_detail.audit_remarks = query['remark']
                slr_detail.person_responsible = employee
                try:
                    slr_detail.compliance_category = compliance_category_value[
                        compliance_value]
                except Exception:
                    slr_detail.compliance_category = ''
                try:
                    slr_detail.compliance_category_percentage = compliance_category_percentage[compliance_category_value[
                        compliance_value]]
                except Exception:
                    slr_detail.compliance_category_percentage = ''
                if query['compliance'] == 'NA':
                    slr_detail.audit_remarks = ''
                if (query['compliance'] and employee) or (query['compliance'] == 'NA'):
                    slr_detail.audit_status = 'Completed'
                if (not query['compliance'] or (not query['compliance'] == 'NA' and not employee)):
                    slr_detail.audit_status = 'Pending'
                slr_detail.save()
                # print(query)
            return JsonResponse({"msg": "success"})
        else:
            return JsonResponse({"msg": "failed"})
    context = {}
    return render(request, "slr_salon/slr_profile_tab.html", context)


def edit_slr_salon_extra_data(request):
    compliance_category_value = {
        "Followed": "RNR",
        "Partially followed": "Benchmark KRA",
        "Couldn't follow": "CPI",
        "Not aware": "Education",
        "Not followed": "PIP",
        "1": "PIP",
        "2": "PIP",
        "3": "PIP",
        "4": "Benchmark KRA",
        "5": "RNR",
        "Like": "RNR",
        "Partially Like": "Benchmark KRA",
        "Dislike": "PIP",
        "Yes": "RNR",
        "No": "PIP",
        "May be": "Benchmark KRA",
        "NA": "NA"
    }
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print(got_query)
        slr_id = got_query[0]['slr_id']
        got_value = got_query[0]['slr_value']
        got_name = got_query[0]['name']

        try:
            slr_query = SlrDetail.objects.get(
                id=int(slr_id))
        except Exception:
            slr_query = None
        if slr_query:
            if got_name == 'user_remark':
                slr_query.audit_remarks = got_value
                slr_query.save()
            if got_name == 'atr_complience':
                slr_query.compliance = got_value
                try:
                    slr_query.compliance_category = compliance_category_value[
                        got_value]
                except Exception:
                    slr_query.compliance_category = ''
                try:
                    slr_query.compliance_category_percentage = compliance_category_percentage[compliance_category_value[
                        got_value]]
                except Exception:
                    slr_query.compliance_category_percentage = ''
                if got_value == 'NA':
                    slr_query.audit_remarks = ''
                if (got_value and slr_query.person_responsible) or (got_value == 'NA'):
                    slr_query.audit_status = 'Completed'
                if (not got_value or (not got_value == 'NA' and not slr_query.person_responsible)):
                    slr_query.audit_status = 'Pending'
                slr_query.save()
            if got_name == 'user_responsible':
                try:
                    got_staff = ExtendedZenotiEmployeesData.objects.get(
                        id=int(got_value))
                except Exception:
                    got_staff = None
                slr_query.person_responsible = got_staff
                slr_query.save()
            if got_name == 'audit_status':
                slr_query.audit_status = got_value
                slr_query.save()
            if got_name == 'comment_auditor':
                slr_query.comment_for_auditor = got_value
                slr_query.save()
            if got_name == 'action_outlet':
                slr_query.action_taken_by_outlet_manager = got_value
                slr_query.save()
            if got_name == 'status_om':
                slr_query.status_by_om = got_value
                slr_query.save()
            if got_name == 'remark_om':
                slr_query.remark_by_om = got_value
                slr_query.save()
            if got_name == 'action_management':
                slr_query.action_taken_by_management = got_value
                slr_query.save()
            if got_name == 'remark_management':
                slr_query.remark_by_management = got_value
                slr_query.save()
            if got_name == 'expected_intervene':
                slr_query.expected_dept_intervene = got_value
                slr_query.save()
            if got_name == 'remark_department':
                slr_query.remark_by_department = got_value
                slr_query.save()
            if got_name == 'status_department':
                slr_query.status_by_department = got_value
                slr_query.save()
            slr_salon_json = serializers.serialize('json', [slr_query])
            return JsonResponse({"msg": "success", "slr_json": json.loads(slr_salon_json)})
        else:
            return JsonResponse({"msg": "failed"})
    return render(request, "slr_salon/slr_overview_tab.html")


def edit_slr_salon_action_required(request):
    compliance_category_value = {
        "Followed": "RNR",
        "Partially followed": "Benchmark KRA",
        "Couldn't follow": "CPI",
        "Not aware": "Education",
        "Not followed": "PIP",
        "1": "PIP",
        "2": "PIP",
        "3": "PIP",
        "4": "Benchmark KRA",
        "5": "RNR",
        "Like": "RNR",
        "Partially Like": "Benchmark KRA",
        "Dislike": "PIP",
        "Yes": "RNR",
        "No": "PIP",
        "May be": "Benchmark KRA",
        "NA": "NA"
    }
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        print(got_query)
        mystery_detail_id = got_query[0]['id']
        if mystery_detail_id:
            try:
                slr_detail_query = SlrDetail.objects.get(
                    id=int(mystery_detail_id))
            except Exception:
                slr_detail_query = None
            try:
                got_user = ExtendedZenotiEmployeesData.objects.get(
                    id=int(got_query[0]['staff']))
            except Exception:
                got_user = None
            compliance_value = got_query[0]['compliance']
            slr_detail_query.compliance = compliance_value
            slr_detail_query.person_responsible = got_user
            slr_detail_query.audit_remarks = got_query[0]['remark']
            try:
                slr_detail_query.compliance_category = compliance_category_value[
                    compliance_value]
            except Exception:
                slr_detail_query.compliance_category = ''
            try:
                slr_detail_query.compliance_category_percentage = compliance_category_percentage[compliance_category_value[
                    compliance_value]]
            except Exception:
                slr_detail_query.compliance_category_percentage = ''
            if (got_query[0]['compliance'] and got_user) or (got_query[0]['compliance'] == 'NA'):
                slr_detail_query.audit_status = 'Action Taken'
            slr_detail_query.save()
            # print(query)
            return JsonResponse({"msg": "success"})
        else:
            return JsonResponse({"msg": "Failed"})


def edit_slr_salon_status_dropdown(request):
    data = json.loads(request.body)
    got_id = data['data_id']
    got_status = data['status']
    if got_id:
        try:
            slr_detail_query = SlrDetail.objects.get(
                id=int(got_id))
        except Exception:
            slr_detail_query = None

        slr_detail_query.audit_status = got_status
        slr_detail_query.save()
        return JsonResponse({"msg": "success"})
    else:
        return JsonResponse({"msg": "failed"})


def edit_slr_salon_reviewed_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print(got_query)
        slr_id = got_query[0]['slr_id']
        got_value = got_query[0]['slr_value'] == 'on'
        got_name = got_query[0]['name']
        # print(got_value)

        try:
            slr_query = SlrAudit.objects.get(
                id=int(slr_id))
        except Exception:
            slr_query = None
        if slr_query:
            if got_name == 'auditor_reviewed':
                slr_query.auditor_action_reviewed = got_value
                slr_query.save()
            if got_name == 'om_reviewed':
                slr_query.om_action_reviewed = got_value
                slr_query.save()
            return JsonResponse({"msg": "success"})
        else:
            return JsonResponse({"msg": "failed"})
    return render(request, "slr_skin/slr_overview_tab.html")