from django.core import serializers  # Import the serializers module
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta, datetime
from .models import MysteryShoppingOverview, MysteryShoppingDetail, MysteryShoppingImages, MonthAudit, MysteryChecklistPersonResponsible
from bc_app.models import UserProfile, ZenotiEmployeesData, ZenotiCentersData, ExtendedZenotiCenterData, ExtendedZenotiEmployeesData, EmployeesLeaveData, UserTypes, MonthAudit, AuditAccess, AuditTypes, CentralAccess
from bc_app.views import sanitize_name, api_key
from bc_app.models import SlrSalonImages
from .forms import MysteryShoppingForm
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, Count
from urllib.request import urlopen
from django.conf import settings
import json
import csv
import requests
from django.http import JsonResponse
from django.core import serializers
# for email
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
# Create your views here.

compliance_category_percentage = {
    "RNR": 100,
    "Benchmark KRA": 50,
    "CPI": 0,
    "PIP": 0,
    "Education": 0
}


@login_required(login_url='user_login')
def audit_users(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    is_audit_admin = staffProfile.user_type_name.filter(
        user_type='Audit Admin').exists()
    is_mystery_shopper = staffProfile.user_type_name.filter(
        user_type='Mystery Shopper').exists()
    is_revenue_auditor = staffProfile.user_type_name.filter(
        user_type='Revenue Auditor').exists()
    is_cyber_security_auditor = staffProfile.user_type_name.filter(
        user_type='Cyber Security Auditor').exists()
    is_corporate_auditor = staffProfile.user_type_name.filter(
        user_type='Corporate Auditor').exists()
    is_slr_auditor = staffProfile.user_type_name.filter(
        user_type='SLR Auditor').exists()
    is_rar_onfloor_auditor = staffProfile.user_type_name.filter(
        user_type='RAR OnFloor Auditor').exists()
    is_rar_oncall_auditor = staffProfile.user_type_name.filter(
        user_type='RAR OnCall Auditor').exists()
    if staffProfile.user_type == 'admin' or is_audit_admin:
        pass
    else:
        return redirect('/')
    audit_user = UserProfile.objects.filter(
        user_type='Auditor')
    all_audit_type = UserTypes.objects.all()
    if request.method == "POST":
        if 'new_audit_user' in request.POST:
            phone = request.POST.get("phone")
            passcode = request.POST.get("passcode")
            name = request.POST.get("name")
            username = request.POST.get("email")
            usertype = request.POST.getlist("user_type")
            is_roster = request.POST.get("is_roster")
            if is_roster == 'on':
                is_roster = True
            else:
                is_roster = False
            try:
                already_user = User.objects.get(username=username)
            except Exception:
                already_user = None
                # print('user', already_user)
            if already_user is None:
                new_user = User.objects.create_user(
                    username=username, password=passcode, first_name=name)
                new_userprofile = UserProfile.objects.create(
                    user=new_user,
                    phone=phone,
                    email=username,
                    password=passcode,
                    user_type='Auditor',
                    user_status='Active',
                    roster_access=is_roster
                )
                selected_user_type = UserTypes.objects.filter(id__in=usertype)
                print(selected_user_type)
                new_userprofile.user_type_name.set(selected_user_type)
            else:
                messages.info(
                    request, 'This Email Id is already exist in our DataBase')
        if 'edit_audit_user' in request.POST:
            user_id = request.POST.get('audit_user_id')
            name = request.POST.get('edit_name')
            phone = request.POST.get('edit_phone')
            email = request.POST.get('edit_email')
            user_type = request.POST.getlist('edit_user_type')
            user_status = request.POST.get('edit_user_status')
            edit_is_roster = request.POST.get("edit_is_roster")
            try:
                audit_user = UserProfile.objects.get(id=int(user_id))
            except Exception:
                audit_user = None

            if edit_is_roster == 'on':
                edit_is_roster = True
            else:
                edit_is_roster = False
            selected_user_type = UserTypes.objects.filter(id__in=user_type)
            audit_user.phone = phone
            audit_user.email = email
            audit_user.user_status = user_status
            audit_user.roster_access = edit_is_roster
            audit_user.user_type_name.set(selected_user_type)
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
        return redirect('audit_users')
    context = {'audit_user': audit_user,
               'staffProfile': staffProfile,
               'is_audit_admin': is_audit_admin,
               'is_mystery_shopper': is_mystery_shopper,
               'is_revenue_auditor': is_revenue_auditor,
               'is_cyber_security_auditor': is_cyber_security_auditor,
               'is_corporate_auditor': is_corporate_auditor,
               'is_slr_auditor': is_slr_auditor,
               'is_rar_onfloor_auditor': is_rar_onfloor_auditor,
               'is_rar_oncall_auditor': is_rar_oncall_auditor,
               'all_audit_type': all_audit_type}
    return render(request, "mystery_shopping/audit_user_page.html", context)


def set_center_correspondence_to_usertype(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        user_type = got_query['val']
        audit_type = got_query['audit_type']
        print(user_type)
        filtered_access = CentralAccess.objects.filter(
            staff__in=[staffProfile], audit__audit_type=audit_type)

        center_dict_set = set()  # Use a set to store unique center dictionaries
        centers = None
        if user_type == 'Audit Admin':
            centers = ExtendedZenotiCenterData.objects.all()

        for each_filtered_access in filtered_access:
            if user_type == 'Auditor':
                centers = each_filtered_access.auditor.all()
            elif user_type == 'Project Owner':
                centers = each_filtered_access.project_owner.all()
            elif user_type == 'Audit Reviewer':
                centers = each_filtered_access.audit_reviewer.all()

        for each_center in centers:
            # center_dict = {
            #     'id': each_center.id,
            #     'name': each_center.zenoti_data.name
            # }
            center_dict_set.add(
                (each_center.id, each_center.zenoti_data.name))

        unique_center_list = [{'id': center_id, 'name': center_name}
                              for center_id, center_name in center_dict_set]
        print('list', unique_center_list)

        if user_type:
            # Return the unique_center_list as JSON response
            return JsonResponse({"msg": "success", "center_json": unique_center_list})
        else:
            return JsonResponse({"msg": "failed"})

    return JsonResponse({"msg": "Invalid request method"})


def edit_audit_user_modal_popup(request):
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
    return render(request, "mystery_shopping/mystery_shopping_tabs_page.html")


def get_user_access_detail(user, audit_type):
    all_center_list = ExtendedZenotiCenterData.objects.all()
    final_access = []
    final_access_kv = {}
    temp_access = []
    filtered_access = CentralAccess.objects.filter(
        staff__in=[user], audit__audit_type=audit_type)
    if user.is_audit_admin or user.is_super_admin:
        final_access.append(['Audit Admin', all_center_list])
        final_access_kv['Audit Admin'] = all_center_list
    for each_filtered_access in filtered_access:
        if each_filtered_access.audit_reviewer.all():
            if 'Audit Reviewer' not in temp_access:
                final_access.append(
                    ['Audit Reviewer', each_filtered_access.audit_reviewer.all()])
                final_access_kv['Audit Reviewer'] = each_filtered_access.audit_reviewer.all(
                )
                temp_access.append('Audit Reviewer')
        if each_filtered_access.project_owner.all():
            if 'Project Owner' not in temp_access:
                final_access.append(
                    ['Project Owner', each_filtered_access.project_owner.all()])
                final_access_kv['Project Owner'] = each_filtered_access.project_owner.all(
                )
                temp_access.append('Project Owner')
        if each_filtered_access.auditor.all():
            if 'Auditor' not in temp_access:
                final_access.append(
                    ['Auditor', each_filtered_access.auditor.all()])
                final_access_kv['Auditor'] = each_filtered_access.auditor.all()
                temp_access.append('Auditor')
    return [final_access, final_access_kv]


def get_invoice_detail_from_zenoti(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        got_invoice_number = data['invoice_number']
        url = 'https://api.zenoti.com/v1/invoices/invoice_id?expand=InvoiceItems&expand=Transactions'
        head = {"Authorization": "apikey "+api_key}
        response = requests.request("GET", url, headers=head)
        response_got = json.loads(response.text)
        print('response', response_got)


@login_required(login_url='user_login')
def mystery_shopping_overview(request):
    current_time = datetime.now().time()
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    all_months = MonthAudit.objects.all()
    selected_center_ids = request.GET.getlist('select_center')
    searched_from_id = request.GET.get('searched_from_id')
    select_audit_status = request.GET.getlist('select_audit_status')
    searched_month = request.GET.getlist('select_month')
    searched_text = request.GET.get('searched_text')
    searched_compliance = request.GET.getlist('searched_compliance')
    searched_kra = request.GET.getlist('searched_kra')
    searched_dept = request.GET.get('searched_dept')
    searched_om = request.GET.get('searched_om')
    searched_management_remark = request.GET.get('searched_management_remark')
    searched_action_by_management = request.GET.getlist(
        'searched_action_by_management')
    searched_personal_intervene = request.GET.getlist(
        'searched_personal_intervene')
    search_imp_checklist = request.GET.get('search_imp_checklist')
    search_user_type = request.GET.get('search_user_type')
    all_employee_query = UserProfile.objects.all().exclude(
        is_super_admin=True).prefetch_related('user')
    all_center = ExtendedZenotiCenterData.objects.filter(
        center_status='Active')
    all_mystery_master = MysteryShoppingOverview.objects.filter(
        is_deleted=False).order_by('-id')
    all_employee_list = []
    is_auditor = False
    is_auditor_reviewer = False
    is_project_owner = False
    is_audit_admin = False

    for each_user in all_employee_query:
        tempUserObj = []
        tempUserObj.append(each_user.id)
        sanitized_first_name = sanitize_name(each_user.user.first_name)
        sanitized_last_name = sanitize_name(each_user.user.last_name)
        tempUserObj.append(f"{sanitized_first_name} {sanitized_last_name}")
        kra_list = []
        for each_role in each_user.associated_role.all():
            kra_list.append(each_role.name)
        tempUserObj.append(kra_list)
        center_list = []
        for each_center in each_user.associated_center.all():
            center_list.append(each_center.id)
        tempUserObj.append(center_list)
        all_employee_list.append(tempUserObj)

    access_detail_ar_kv = get_user_access_detail(
        staffProfile, 'Mystery Shopper')
    access_detail = access_detail_ar_kv[0]
    access_detail_kv = access_detail_ar_kv[1]
    if len(access_detail) == 0:
        return JsonResponse({"msg": "You Dont HAve access to the Mystery Shopping"})
    this_user_type = search_user_type
    if not this_user_type:
        this_user_type = access_detail[0][0]
    this_location = access_detail_kv[this_user_type]
    all_mystery = MysteryShoppingOverview.objects.none()
    mystery_form = MysteryShoppingForm(request.POST or None)
    mystery_form.fields['center'].queryset = this_location
    if this_user_type == 'Audit Admin':
        all_mystery = all_mystery_master
        if selected_center_ids:
            all_center = all_center.filter(id__in=selected_center_ids)
            all_mystery = all_mystery_master.filter(center__in=all_center)
    if this_user_type == 'Audit Reviewer':
        if not selected_center_ids:
            all_center = this_location
        else:
            all_center = all_center.filter(id__in=selected_center_ids)
        all_mystery = all_mystery_master.filter(center__in=all_center)
    if this_user_type == 'Project Owner':
        if not selected_center_ids:
            all_center = this_location
        else:
            all_center = all_center.filter(id__in=selected_center_ids)
        all_mystery = all_mystery_master.filter(
            center__in=all_center, auditor_action_reviewed=True)
    if this_user_type == 'Auditor':
        if not selected_center_ids:
            all_mystery = all_mystery_master.filter(
                Q(added_by=staffProfile) | Q(auditor_access_to=staffProfile), is_deleted=False).distinct()
        else:
            all_center = all_center.filter(id__in=selected_center_ids)
            all_mystery = all_mystery_master.filter(
                Q(added_by=staffProfile) | Q(auditor_access_to=staffProfile), center__in=all_center, is_deleted=False).distinct()
        # print('.....', all_reviewed_mystery)

    all_mystery_detail = MysteryShoppingDetail.objects.filter(
        mystery_shopping__in=all_mystery)
    all_mystery_image = MysteryShoppingImages.objects.filter(
        mystery_shopping__in=all_mystery)
    all_user_responsible = MysteryChecklistPersonResponsible.objects.filter(
        mystery_checklist__in=all_mystery_detail)

    unique_kra_fieled = MysteryShoppingDetail.objects.order_by(
    ).values_list('kra', flat=True).distinct()
    unique_process_fieled = MysteryShoppingDetail.objects.order_by(
    ).values_list('process', flat=True).distinct()

    try:
        selected_month = MonthAudit.objects.filter(id__in=searched_month)
    except Exception:
        selected_month = None

    if searched_from_id:
        all_mystery = all_mystery.filter(id=int(searched_from_id))
        all_mystery_detail = all_mystery_detail.filter(
            mystery_shopping__in=all_mystery)
        all_mystery_image = all_mystery_image.filter(
            mystery_shopping__in=all_mystery)
        all_user_responsible = all_user_responsible.filter(
            mystery_checklist__in=all_mystery_detail)

    if select_audit_status:
        if 'All' in select_audit_status:
            all_mystery_detail = MysteryShoppingDetail.objects.filter(mystery_shopping__in=all_mystery,
                                                                      audit_status__in=['Completed', 'Pending'])
        else:
            all_mystery_detail = MysteryShoppingDetail.objects.filter(mystery_shopping__in=all_mystery,
                                                                      audit_status__in=select_audit_status)
        all_user_responsible = all_user_responsible.filter(
            mystery_checklist__in=all_mystery_detail)

    if selected_month:
        # print('month', selected_month)
        all_mystery = all_mystery.filter(
            month_of_audit__in=selected_month)
        all_mystery_detail = all_mystery_detail.filter(
            mystery_shopping__in=all_mystery)
        all_mystery_image = all_mystery_image.filter(
            mystery_shopping__in=all_mystery)
        all_user_responsible = all_user_responsible.filter(
            mystery_checklist__in=all_mystery_detail)

    if searched_compliance:
        all_user_responsible = all_user_responsible.filter(
            compliance_category__in=searched_compliance)
        compliance_filtered_user_resp_ids = all_user_responsible.values(
            'mystery_checklist__id')
        all_mystery_detail = all_mystery_detail.filter(
            id__in=compliance_filtered_user_resp_ids)

    if searched_kra:
        all_mystery_detail = all_mystery_detail.filter(
            kra__in=searched_kra)
        all_user_responsible = all_user_responsible.filter(
            mystery_checklist__in=all_mystery_detail)

    if searched_om:
        all_user_responsible = all_user_responsible.filter(
            status_by_om=searched_om)
        om_filtered_user_resp_ids = all_user_responsible.values(
            'mystery_checklist__id')
        all_mystery_detail = all_mystery_detail.filter(
            id__in=om_filtered_user_resp_ids
        )
    if searched_dept:
        all_user_responsible = all_user_responsible.filter(
            status_by_department=searched_dept)
        dept_filtered_user_resp_ids = all_user_responsible.values(
            'mystery_checklist__id')
        all_mystery_detail = all_mystery_detail.filter(
            id__in=dept_filtered_user_resp_ids
        )
    if searched_action_by_management:
        all_user_responsible = all_user_responsible.filter(
            action_taken_by_management__in=searched_action_by_management)
        action_by_management_filtered_user_resp_ids = all_user_responsible.values(
            'mystery_checklist__id')
        all_mystery_detail = all_mystery_detail.filter(
            id__in=action_by_management_filtered_user_resp_ids
        )
    if searched_personal_intervene:
        all_user_responsible = all_user_responsible.filter(
            expected_dept_intervene__in=searched_personal_intervene)
        personal_intervene_filtered_user_resp_ids = all_user_responsible.values(
            'mystery_checklist__id')
        all_mystery_detail = all_mystery_detail.filter(
            id__in=personal_intervene_filtered_user_resp_ids
        )
    if searched_management_remark:
        all_user_responsible = all_user_responsible.filter(
            remark_by_management__icontains=searched_management_remark)
        management_remark_filtered_user_resp_ids = all_user_responsible.values(
            'mystery_checklist__id')
        all_mystery_detail = all_mystery_detail.filter(
            id__in=management_remark_filtered_user_resp_ids
        )
    if search_imp_checklist:
        if search_imp_checklist == 'Important':
            all_user_responsible = all_user_responsible.filter(
                is_important=True)
            imp_checklist_filtered_user_resp_ids = all_user_responsible.values(
                'mystery_checklist__id')
            all_mystery_detail = all_mystery_detail.filter(
                id__in=imp_checklist_filtered_user_resp_ids)
        if search_imp_checklist == 'Not Important':
            all_user_responsible = all_user_responsible.filter(
                is_important=False)
            imp_checklist_filtered_user_resp_ids = all_user_responsible.values(
                'mystery_checklist__id')
            all_mystery_detail = all_mystery_detail.filter(
                id__in=imp_checklist_filtered_user_resp_ids)
    page = Paginator(all_mystery, 20)
    list_page_num = request.GET.get('page', 1)
    try:
        list_page_query = page.page(list_page_num)
    except EmptyPage:
        list_page_query = page.page(1)

    list_start_index = (int(list_page_num) - 1) * page.per_page + 1
    list_end_index = min(list_start_index + page.per_page - 1, page.count)
    list_page = []
    for overview in list_page_query:
        all_not_blank_question = MysteryShoppingDetail.objects.filter(
            mystery_shopping=overview).exclude(audit_status='')
        total_completed = all_not_blank_question.filter(
            audit_status='Completed')
        total_pending = all_not_blank_question.filter(
            audit_status='Pending')
        all_person_resp = MysteryChecklistPersonResponsible.objects.filter(
            mystery_checklist__mystery_shopping=overview)
        total_action_required = all_person_resp.filter(
            action_status='Action Required')
        total_action_taken = all_person_resp.filter(
            action_status='Action Taken')
        not_rnr = all_person_resp.filter(
            Q(compliance_category_percentage='0') | Q(compliance_category_percentage='50'))
        om_actioned = not_rnr.filter(action_taken_by_outlet_manager__isnull=False,
                                     status_by_om__isnull=False, remark_by_om__isnull=False).exclude(action_taken_by_outlet_manager='').exclude(status_by_om='').exclude(remark_by_om='')
        try:
            month_audit = overview.month_of_audit.month
        except Exception:
            month_audit = None
        try:
            month_audit_id = overview.month_of_audit.id
        except Exception:
            month_audit_id = None
        temp = {}
        temp['id'] = overview.id
        temp['added_by'] = overview.added_by.user.first_name
        temp['added_on'] = overview.added_on
        temp['shopper_name'] = overview.shopper_name
        temp['month_audit'] = month_audit
        temp['month_audit_id'] = month_audit_id
        temp['date'] = overview.date
        temp['start_time'] = overview.start_time
        temp['end_time'] = overview.end_time
        temp['center'] = overview.center.zenoti_data.name
        temp['center_id'] = overview.center.id
        temp['total_question'] = len(all_not_blank_question)
        temp['total_completed_question'] = len(total_completed)
        temp['total_pending_question'] = len(total_pending)
        temp['total_action_required_question'] = len(total_action_required)
        temp['total_action_taken_question'] = len(total_action_taken)
        temp['not_rnr'] = len(not_rnr)
        temp['om_actioned'] = len(om_actioned)
        try:
            s1 = overview.service_availed_1
        except Exception:
            s1 = ''
        if s1 is None:
            s1 = ''
        try:
            s2 = overview.service_availed_2
        except Exception:
            s2 = ''
        if s2 is None:
            s2 = ''
        try:
            s3 = overview.service_availed_3
        except Exception:
            s3 = ''
        if s3 is None:
            s3 = ''
        temp['service_availed'] = (s1 + '\n' + s2 + '\n' + s3).strip()
        temp['cost_of_service'] = overview.cost_of_service
        temp['invoice_number'] = overview.invoice_number
        temp['auditor_action_reviewed'] = overview.auditor_action_reviewed
        temp['om_action_reviewed'] = overview.om_action_reviewed
        list_page.append(temp)
    # detail pagination
    page_2 = Paginator(all_mystery_detail, 50)
    detail_page_num = request.GET.get('page_2', 1)
    try:
        detail_page_query = page_2.page(detail_page_num)
    except EmptyPage:
        detail_page_query = page_2.page(1)
    detail_start_index = (int(detail_page_num) - 1) * page_2.per_page + 1
    detail_end_index = min(detail_start_index +
                           page_2.per_page - 1, page_2.count)

    page_3 = Paginator(all_mystery_image, 20)
    image_page_num = request.GET.get('page_3', 1)
    try:
        image_page = page_3.page(image_page_num)
    except EmptyPage:
        image_page = page_3.page(1)
    print('this_user', this_user_type)
    if this_user_type == 'Audit Admin':
        is_audit_admin = True
    if this_user_type == 'Audit Reviewer':
        is_auditor_reviewer = True
    if this_user_type == 'Project Owner':
        is_project_owner = True
    if this_user_type == 'Auditor':
        is_auditor = True
    # print('center', selected_center_ids)
    if request.method == 'POST':
        data_json = open("mistery_data.txt", "r")
        mystery_detail_data = json.loads(data_json.read())
        if 'mystery_form' in request.POST:
            if mystery_form.is_valid():
                new_mystery = mystery_form.save(commit=False)
                service_agent_id_1 = request.POST.get('add_service_agent_1')
                service_agent_id_2 = request.POST.get('add_service_agent_2')
                service_agent_id_3 = request.POST.get('add_service_agent_3')
                auditor_ids = request.POST.getlist('add_auditor_access_to')
                try:
                    agent_1 = UserProfile.objects.get(
                        id=int(service_agent_id_1))
                except Exception:
                    agent_1 = None
                try:
                    agent_2 = UserProfile.objects.get(
                        id=int(service_agent_id_2))
                except Exception:
                    agent_2 = None
                try:
                    agent_3 = UserProfile.objects.get(
                        id=int(service_agent_id_3))
                except Exception:
                    agent_3 = None
                try:
                    auditors_query = UserProfile.objects.filter(
                        id__in=auditor_ids)
                except Exception:
                    auditors_query = None
                print('audittt', auditor_ids, auditors_query)

                new_mystery.added_by = staffProfile
                new_mystery.service_agent_1 = agent_1
                new_mystery.service_agent_2 = agent_2
                new_mystery.service_agent_3 = agent_3
                new_mystery.save()
                new_mystery.auditor_access_to.set(auditors_query)
                new_mystery.save()
                for overview in mystery_detail_data:
                    # print(type(overview['service_number']))
                    if overview['service_number'] == "1":
                        service_responsible = new_mystery.service_agent_1
                    elif overview['service_number'] == "2":
                        service_responsible = new_mystery.service_agent_2
                    elif overview['service_number'] == "3":
                        service_responsible = new_mystery.service_agent_3
                    else:
                        service_responsible = None
                    # status = 'Pending'
                    if (overview['service_number'] == '1' and new_mystery.service_availed_1 and new_mystery.service_agent_1) or (overview['service_number'] == '2' and new_mystery.service_availed_2 and new_mystery.service_agent_2) or (overview['service_number'] == '3' and new_mystery.service_availed_3 and new_mystery.service_agent_3) or (overview['service_number'] == ''):
                        audit_status = 'Pending'
                    else:
                        # continue
                        audit_status = ''
                    # print('ser', service_responsible)
                    new_mystery_detail = MysteryShoppingDetail.objects.create(
                        mystery_shopping=new_mystery,
                        sequence=overview['sequence'],
                        client_journey=overview['client_journey'],
                        kra=overview['kra'],
                        process=overview['process'],
                        checklist=overview['checklist'],
                        relative_gaps_found=overview['relative_gaps_found'],
                        compliance_dropdown=overview['dropdown'],
                        service_number=overview['service_number'],
                        minimum_person_responsible=overview['minimum_pr'],
                        audit_status=audit_status
                    )

                    if overview['service_number'] in ['1', '2', '3']:
                        # print(
                        #     'in', overview['service_number'], service_responsible)
                        MysteryChecklistPersonResponsible.objects.create(
                            mystery_checklist=new_mystery_detail,
                            staff=service_responsible,
                            # service_number=overview['service_number'],
                        )

        if 'del_mystery' in request.POST:
            del_mystery_id = request.POST.get('del_id')
            try:
                mystery_shopping = MysteryShoppingOverview.objects.get(
                    id=int(del_mystery_id))
            except Exception:
                mystery_shopping = None

            mystery_shopping.is_deleted = True
            mystery_shopping.save()
        if 'edit_mystery' in request.POST:
            mystery_id = request.POST.get('mystery_pk')
            center_id = request.POST.get('edit_center')
            shopper_name = request.POST.get('edit_shopper_name')
            phone = request.POST.get('edit_phone')
            email = request.POST.get('edit_email')
            gender = request.POST.get('edit_gender')
            start_time = request.POST.get('edit_start')
            end_time = request.POST.get('edit_end')
            month_id = request.POST.get('edit_month')
            date = request.POST.get('edit_date')
            cost_of_service = request.POST.get('edit_cost_of_service')
            invoice_number = request.POST.get('edit_invoice_number')
            paid_in_cash = request.POST.get('edit_paid_cash')
            payment_mode = request.POST.get('edit_payment_mode')
            amount_redeemed = request.POST.get('edit_amount_redeemed')
            number_reached = request.POST.get('edit_number_reached')
            service_availed_1 = request.POST.get('edit_service_av_1')
            service_agent_id_1 = request.POST.get('edit_service_ag_1')
            service_availed_2 = request.POST.get('edit_service_av_2')
            service_agent_id_2 = request.POST.get('edit_service_ag_2')
            service_availed_3 = request.POST.get('edit_service_av_3')
            service_agent_id_3 = request.POST.get('edit_service_ag_3')
            auditor_ids = request.POST.getlist('edit_auditor_access_to')

            if start_time == '':
                starting_time = None
            else:
                starting_time = start_time
            if end_time == '':
                ending_time = None
            else:
                ending_time = end_time

            try:
                mystery = MysteryShoppingOverview.objects.get(
                    id=int(mystery_id))
            except Exception:
                mystery = None

            try:
                center = ExtendedZenotiCenterData.objects.get(
                    id=int(center_id))
            except Exception:
                center = None

            try:
                mystery_detail = MysteryShoppingDetail.objects.filter(
                    mystery_shopping=mystery)
            except Exception:
                mystery_detail = None

            try:
                mystery_files = MysteryShoppingImages.objects.filter(
                    mystery_shopping=mystery)
            except Exception:
                mystery_files = None

            try:
                month_query = MonthAudit.objects.get(id=int(month_id))
            except Exception:
                month_query = None

            try:
                agent_1 = UserProfile.objects.get(
                    id=int(service_agent_id_1))
            except Exception:
                agent_1 = None
            try:
                agent_2 = UserProfile.objects.get(
                    id=int(service_agent_id_2))
            except Exception:
                agent_2 = None
            try:
                agent_3 = UserProfile.objects.get(
                    id=int(service_agent_id_3))
            except Exception:
                agent_3 = None

            try:
                auditors_query = UserProfile.objects.filter(id__in=auditor_ids)
            except Exception:
                auditors_query = None

            mystery.center = center
            mystery.shopper_name = shopper_name
            mystery.mobile = phone
            mystery.email = email
            mystery.gender = gender
            mystery.start_time = starting_time
            mystery.end_time = ending_time
            mystery.month_of_audit = month_query
            mystery.date = date
            mystery.cost_of_service = cost_of_service
            mystery.invoice_number = invoice_number
            mystery.paid_in_cash = paid_in_cash
            mystery.payment_mode = payment_mode
            mystery.amount_redeemed = amount_redeemed
            mystery.contact_number_reached_for_appointment = number_reached
            mystery.service_availed_1 = service_availed_1
            mystery.service_agent_1 = agent_1
            mystery.service_availed_2 = service_availed_2
            mystery.service_agent_2 = agent_2
            mystery.service_availed_3 = service_availed_3
            mystery.service_agent_3 = agent_3
            mystery.auditor_access_to.set(auditors_query)
            mystery.save()

            for each_detail in mystery_detail:
                try:
                    mystery_user_resp = MysteryChecklistPersonResponsible.objects.filter(
                        mystery_checklist=each_detail
                    ).first()
                except Exception:
                    mystery_user_resp = None
                # print('ms', mystery_user_resp)
                if mystery_user_resp:
                    if each_detail.service_number == '1':
                        mystery_user_resp.staff = mystery.service_agent_1
                    if each_detail.service_number == '2':
                        mystery_user_resp.staff = mystery.service_agent_2
                    if each_detail.service_number == '3':
                        mystery_user_resp.staff = mystery.service_agent_3
                    mystery_user_resp.save()

                if ((each_detail.service_number == '1' and mystery.service_availed_1 and mystery.service_agent_1) or (each_detail.service_number == '2' and mystery.service_availed_2 and mystery.service_agent_2) or (each_detail.service_number == '3' and mystery.service_availed_3 and mystery.service_agent_3)) and len(each_detail.audit_status) < 3:
                    each_detail.audit_status = 'Pending'

                if ((each_detail.service_number == '1' and (not mystery.service_availed_1 or not mystery.service_agent_1)) or (each_detail.service_number == '2' and (not mystery.service_availed_2 or not mystery.service_agent_2)) or (each_detail.service_number == '3' and (not mystery.service_availed_3 or not mystery.service_agent_3))) and each_detail.audit_status:
                    each_detail.audit_status = ''
                    each_detail.comment_for_auditor = ''
                    each_detail.compliance = ''
                    each_detail.compliance_category = ''
                    each_detail.compliance_category_percentage = ''
                    each_detail.remark = ''
                    if mystery_user_resp:
                        mystery_user_resp.staff = None
                        mystery_user_resp.save()
                    # each_detail.staff = None
                    each_detail.remark_by_om = ''
                    each_detail.action_taken_by_outlet_manager = ''
                    each_detail.status_by_om = ''
                    each_detail.action_taken_by_management = ''
                    each_detail.remark_by_management = ''
                    each_detail.expected_dept_intervene = ''
                    each_detail.remark_by_department = ''
                    each_detail.status_by_department = ''
                each_detail.save()
        if 'mystery_csv' in request.POST:
            csv_headers = [
                'Mystery ID', 'Checklist ID', 'Series No', 'Center', 'Month of Audit', 'Client Journey', 'KRA', 'Process', 'Checklist', 'Compliance', 'Compliance Category', 'Compliance Category Percentage', 'Relative Gaps Found', 'User Responsible', 'Service Availed', 'Remark By Auditor', 'Action Taken By Outlet Manager', 'Status By Om', 'Remark By OM', 'Action Taken By Management', 'Remark By Management', 'Expected Dept/Personnel to Intervene', 'Remark By Department', 'Status By Department'
            ]
            rows = []

            for each_detail in all_mystery_detail:
                service_availed = ''
                if each_detail.service_number == '1':
                    service_availed = each_detail.service_availed_1
                elif each_detail.service_number == '2':
                    service_availed = each_detail.service_availed_2
                elif each_detail.service_number == '3':
                    service_availed = each_detail.service_availed_3
                else:
                    service_availed = each_detail.service_availed_1, each_detail.service_availed_2, each_detail.service_availed_3
                try:
                    user_responsible = each_detail.staff.zenoti_data.employee_name
                except Exception:
                    user_responsible = ''

                try:
                    month_audit = each_detail.mystery_shopping.month_of_audit.month
                except Exception:
                    month_audit = ''
                rows.append([
                    each_detail.mystery_shopping.id,
                    each_detail.id,
                    each_detail.service_number,
                    each_detail.center.zenoti_data.name,
                    month_audit,
                    each_detail.client_journey,
                    each_detail.kra,
                    each_detail.process,
                    each_detail.checklist,
                    each_detail.compliance,
                    each_detail.compliance_category,
                    each_detail.compliance_category_percentage,
                    each_detail.relative_gaps_found,
                    user_responsible,
                    service_availed,
                    each_detail.remark,
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
                'mystery_shopping_atr-' + str(datetime.today().date()) + '.csv')
            writer = csv.writer(csv_response)
            writer.writerow(csv_headers)
            writer.writerows(rows)
            print('response', csv_response)
            return csv_response
        if 'mystery_overview_csv' in request.POST:
            csv_headers = [
                'ID', 'Added By', 'Center', 'Shopper Name', 'Mobile', 'Email', 'Gender', 'Month of Audit', 'Date', 'Start time', 'End time', 'Cost of Service', 'Invoice Number', 'Paid in Cash', 'Amount Redeemed', 'Contact Reached for Apointment', 'Service Availed 1', 'Service Agent 1', 'Service Availed 2', 'Service Agent 2', 'Service Availed 3', 'service Agent 3', 'Auditor Action Reviewed', 'OM Action Reviewed'
            ]
            rows = []
            for each_mystery in all_mystery:
                try:
                    added_by = each_mystery.added_by.user.first_name
                except Exception:
                    added_by = ''
                try:
                    month_audit = each_mystery.month_of_audit.month
                except Exception:
                    month_audit = ''

                try:
                    service_agent_1 = each_mystery.service_agent_1.user.first_name + \
                        ' ' + each_mystery.service_agent_1.user.last_name
                except Exception:
                    service_agent_1 = ''
                try:
                    service_agent_2 = each_mystery.service_agent_2.user.first_name + \
                        ' ' + each_mystery.service_agent_2.user.last_name
                except Exception:
                    service_agent_2 = ''
                try:
                    service_agent_3 = each_mystery.service_agent_3.user.first_name + \
                        ' ' + each_mystery.service_agent_3.user.last_name
                except Exception:
                    service_agent_3 = ''
                rows.append([
                    each_mystery.id,
                    added_by,
                    each_mystery.center.zenoti_data.name,
                    each_mystery.shopper_name,
                    each_mystery.mobile,
                    each_mystery.email,
                    each_mystery.gender,
                    month_audit,
                    each_mystery.date,
                    each_mystery.start_time,
                    each_mystery.end_time,
                    each_mystery.cost_of_service,
                    each_mystery.invoice_number,
                    each_mystery.paid_in_cash,
                    each_mystery.amount_redeemed,
                    each_mystery.contact_number_reached_for_appointment,
                    each_mystery.service_availed_1,
                    service_agent_1,
                    each_mystery.service_availed_2,
                    service_agent_2,
                    each_mystery.service_availed_3,
                    service_agent_3,
                    each_mystery.auditor_action_reviewed,
                    each_mystery.om_action_reviewed
                ])
            csv_response = HttpResponse(content_type='text/csv')

            csv_response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
                'mystery_shopping_list-' + str(datetime.today().date()) + '.csv')
            writer = csv.writer(csv_response)
            writer.writerow(csv_headers)
            writer.writerows(rows)
            print('response', csv_response)
            return csv_response

        return redirect('mystery_shopping')
    context = {'all_mystery': list_page,
               'list_page_query': list_page_query,
               'staffProfile': staffProfile,
               'access_detail': access_detail,
               'is_audit_admin': is_audit_admin,
               'is_project_owner': is_project_owner,
               'is_auditor': is_auditor,
               'is_auditor_reviewer': is_auditor_reviewer,
               'this_user_type': this_user_type,
               'all_user_responsible': all_user_responsible,
               'mystery_form': mystery_form,
               'center_corresponding_user_type': this_location,
               'all_mystery_detail': detail_page_query,
               'detail_page_query': detail_page_query,
               'all_mystery_image': image_page,
               'selected_center_id': selected_center_ids,
               'list_start_index': list_start_index,
               'list_end_index': list_end_index,
               'list_total': page.count,
               'detail_start_index': detail_start_index,
               'detail_end_index': detail_end_index,
               'detail_total': page_2.count,
               'select_audit_status': select_audit_status,
               'searched_month': searched_month,
               'searched_text': searched_text,
               'searched_management_remark': searched_management_remark,
               'searched_action_by_management': searched_action_by_management,
               'searched_personal_intervene': searched_personal_intervene,
               'search_imp_checklist': search_imp_checklist,
               'searched_from_id': searched_from_id,
               'searched_compliance': searched_compliance,
               'unique_kra_filed': unique_kra_fieled,
               'unique_process_fieled': unique_process_fieled,
               'searched_kra': searched_kra,
               'searched_dept': searched_dept,
               'searched_om': searched_om,
               'all_months': all_months,
               'all_employee_list': all_employee_list,
               'search_user_type': search_user_type}
    return render(request, "mystery_shopping/mystery_shopping_tabs_page.html", context)


def edit_mystery_reviewed_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print(got_query)
        mystery_id = got_query[0]['mystery_id']
        got_value = got_query[0]['mystery_value'] == 'on'
        got_name = got_query[0]['name']
        print(got_value)

        try:
            mystery_query = MysteryShoppingOverview.objects.get(
                id=int(mystery_id))
        except Exception:
            mystery_query = None
        if mystery_query:
            if got_name == 'auditor_reviewed':
                mystery_query.auditor_action_reviewed = got_value
                mystery_query.save()
            if got_name == 'om_reviewed':
                mystery_query.om_action_reviewed = got_value
                mystery_query.save()
            return JsonResponse({"msg": "success"})
        else:
            return JsonResponse({"msg": "failed"})
    return render(request, "mystery_shopping/mystery_shopping_tabs_page.html")


def mark_important_chcklist(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_id = data['data_obj']
        # print(got_query)
        try:
            checklist_query = MysteryChecklistPersonResponsible.objects.get(
                id=int(got_id))
        except Exception:
            checklist_query = None
        if checklist_query:
            if checklist_query.is_important == True:
                checklist_query.is_important = False
                checklist_query.save()
            else:
                checklist_query.is_important = True
                checklist_query.save()
            return JsonResponse({"msg": "success"})
        else:
            return JsonResponse({"msg": "failed"})


@login_required(login_url='user_login')
def mystery_shopping_detail(request, pk):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    try:
        mystery_shopping = MysteryShoppingOverview.objects.get(id=int(pk))
    except Exception:
        mystery_shopping = None
    all_images_list = MysteryShoppingImages.objects.filter(
        mystery_shopping=mystery_shopping)
    all_employee = ExtendedZenotiEmployeesData.objects.filter(
        associated_center=mystery_shopping.center)
    all_mystery_detail = MysteryShoppingDetail.objects.filter(
        ~Q(kra='Service Agent'), mystery_shopping=mystery_shopping)
    all_user_responsible_profile = MysteryChecklistPersonResponsible.objects.filter(
        mystery_checklist__in=all_mystery_detail)
    all_service_agent_mystery_detail_1 = MysteryShoppingDetail.objects.filter(
        mystery_shopping=mystery_shopping, kra='Service Agent', service_number='1')
    all_user_responsible_s1 = MysteryChecklistPersonResponsible.objects.filter(
        mystery_checklist__in=all_service_agent_mystery_detail_1)
    all_service_agent_mystery_detail_2 = MysteryShoppingDetail.objects.filter(
        mystery_shopping=mystery_shopping, kra='Service Agent', service_number='2')
    all_user_responsible_s2 = MysteryChecklistPersonResponsible.objects.filter(
        mystery_checklist__in=all_service_agent_mystery_detail_2)
    all_service_agent_mystery_detail_3 = MysteryShoppingDetail.objects.filter(
        mystery_shopping=mystery_shopping, kra='Service Agent', service_number='3')
    all_user_responsible_s3 = MysteryChecklistPersonResponsible.objects.filter(
        mystery_checklist__in=all_service_agent_mystery_detail_3)
    # all_therapy_emp = ZenotiEmployeesData.objects.filter(job_info='Therapist')
    # all_therapy_ext_emp = ExtendedZenotiEmployeesData.objects.all()
    all_users_query = UserProfile.objects.all().exclude(
        is_super_admin=True).prefetch_related('user')
    all_employee_list = []
    for each_user in all_users_query:
        tempUserObj = []
        tempUserObj.append(each_user.id)
        sanitized_first_name = sanitize_name(each_user.user.first_name)
        sanitized_last_name = sanitize_name(each_user.user.last_name)
        tempUserObj.append(f"{sanitized_first_name} {sanitized_last_name}")
        kra_list = []
        for each_role in each_user.associated_role.all():
            kra_list.append(each_role.name)
        tempUserObj.append(kra_list)
        center_list = []
        for each_center in each_user.associated_center.all():
            center_list.append(each_center.id)
        tempUserObj.append(center_list)
        all_employee_list.append(tempUserObj)
    # print('user', all_employee_list)
    if request.method == 'POST':
        if 'image_submit' in request.POST:
            description = request.POST.get('desc')
            image = request.FILES["selected_img"]
            MysteryShoppingImages.objects.create(
                mystery_shopping=mystery_shopping,
                description=description,
                image=image
            )
            print(image)
        if 'image_delete' in request.POST:
            img_id = request.POST.get('img_id')
            try:
                mystery_image = MysteryShoppingImages.objects.get(
                    id=int(img_id))
            except Exception:
                mystery_image = None
            mystery_image.delete()
        if 'user_resp_delete' in request.POST:
            user_resp_id = request.POST.get('user_del_id')
            try:
                user_resp = MysteryChecklistPersonResponsible.objects.get(
                    id=int(user_resp_id))
            except Exception:
                user_resp = None
            user_resp.delete()

        return redirect('mystery_shopping_detail', pk=pk)
    context = {'all_audit_detail': all_mystery_detail,
               'staffProfile': staffProfile,
               'all_user_responsible_profile': all_user_responsible_profile,
               'all_employee': all_employee,
               'total_length': all_mystery_detail.count(),
               'total_service_agent_length': all_service_agent_mystery_detail_1.count(),
               'audit_query': mystery_shopping,
               'all_service_agent_mystery_detail_1': all_user_responsible_s1,
               'all_service_agent_mystery_detail_2': all_user_responsible_s2,
               'all_service_agent_mystery_detail_3': all_user_responsible_s3,
               'all_images_list': all_images_list,
               'all_employee_list': all_employee_list,
               'audit_type': 'Mystery Shopping'}
    return render(request, "mystery_shopping/mystery_shopping_profile.html", context)


def edit_mystery_shopping_action_required(request):
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
        mystery_detail_user_response_id = got_query[0]['id']
        if mystery_detail_user_response_id:
            try:
                user_responsible_query = MysteryChecklistPersonResponsible.objects.get(
                    id=int(mystery_detail_user_response_id))
            except Exception:
                user_responsible_query = None
            try:
                got_user = UserProfile.objects.get(
                    id=int(got_query[0]['staff']))
            except Exception:
                got_user = None
            compliance_value = got_query[0]['compliance']
            user_responsible_query.compliance = compliance_value
            user_responsible_query.staff = got_user
            user_responsible_query.remark = got_query[0]['remark']
            try:
                user_responsible_query.compliance_category = compliance_category_value[
                    compliance_value]
            except Exception:
                user_responsible_query.compliance_category = ''
            try:
                user_responsible_query.compliance_category_percentage = compliance_category_percentage[compliance_category_value[
                    compliance_value]]
            except Exception:
                user_responsible_query.compliance_category_percentage = ''
            if (got_query[0]['compliance'] and got_user) or (got_query[0]['compliance'] == 'NA'):
                user_responsible_query.action_status = 'Action Taken'
            user_responsible_query.save()
            # print(query)
            return JsonResponse({"msg": "success"})
        else:
            return JsonResponse({"msg": "Failed"})


def edit_mystery_shopping_profile(request):
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
                person_responsible_query = MysteryChecklistPersonResponsible.objects.get(
                    id=int(query['id']))
                try:
                    employee = UserProfile.objects.get(id=query['staff'])
                except Exception:
                    employee = None
                all_person_responsible_query_of_this_checklist = MysteryChecklistPersonResponsible.objects.filter(
                    mystery_checklist=person_responsible_query.mystery_checklist)
                compliance_value = query['compliance']
                person_responsible_query.compliance = query['compliance']
                person_responsible_query.remark = query['remark']
                person_responsible_query.staff = employee
                try:
                    person_responsible_query.compliance_category = compliance_category_value[
                        compliance_value]
                except Exception:
                    person_responsible_query.compliance_category = ''
                try:
                    person_responsible_query.compliance_category_percentage = compliance_category_percentage[compliance_category_value[
                        compliance_value]]
                except Exception:
                    person_responsible_query.compliance_category_percentage = ''
                if query['compliance'] == 'NA':
                    person_responsible_query.remark = ''
                if (query['compliance'] and employee) or (query['compliance'] == 'NA'):
                    if len(all_person_responsible_query_of_this_checklist) > int(person_responsible_query.mystery_checklist.minimum_person_responsible):
                        person_responsible_query.mystery_checklist.audit_status = 'Completed'
                    else:
                        person_responsible_query.mystery_checklist.audit_status = 'Pending'
                if (not query['compliance'] or (not query['compliance'] == 'NA' and not employee)):
                    person_responsible_query.mystery_checklist.audit_status = 'Pending'
                person_responsible_query.mystery_checklist.save()
                person_responsible_query.save()
                # print(query)
            return JsonResponse({"msg": "success"})
        else:
            return JsonResponse({"msg": "failed"})
    context = {}
    return render(request, "mystery_shopping/mystery_shopping_profile.html", context)


def edit_mystery_shopping(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print("data", got_query)
        try:
            mystery_shopping = MysteryShoppingOverview.objects.get(
                id=int(got_query))
        except Exception:
            mystery_shopping = None

        mystery_json = serializers.serialize('json', [mystery_shopping])
        all_employee = UserProfile.objects.all().exclude(user__is_superuser=True)
        all_emp_list = []
        for each_employee in all_employee:
            tempUserObj = {}
            tempUserObj["id"] = each_employee.id
            sanitized_first_name = sanitize_name(each_employee.user.first_name)
            sanitized_last_name = sanitize_name(each_employee.user.last_name)
            tempUserObj["name"] = f"{sanitized_first_name} {sanitized_last_name}"
            all_emp_list.append(tempUserObj)
        return JsonResponse({"msg": "success",
                            "mystery_json": json.loads(mystery_json), 'user_json': all_emp_list})
    return render(request, "mystery_shopping/mystery_shopping_tabs_page.html")


def edit_mystery_extra_data(request):
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
        mystery_id = got_query[0]['mystery_id']
        got_value = got_query[0]['mystery_value']
        got_name = got_query[0]['name']
        staff_name = None

        try:
            person_responsible_query = MysteryChecklistPersonResponsible.objects.get(
                id=int(mystery_id))
        except Exception:
            person_responsible_query = None
        all_person_responsible_query_of_this_checklist = MysteryChecklistPersonResponsible.objects.filter(
            mystery_checklist=person_responsible_query.mystery_checklist)
        if person_responsible_query:
            if got_name == 'user_remark':
                person_responsible_query.remark = got_value
                person_responsible_query.save()
            if got_name == 'atr_complience':
                person_responsible_query.compliance = got_value
                try:
                    person_responsible_query.compliance_category = compliance_category_value[
                        got_value]
                except Exception:
                    person_responsible_query.compliance_category = ''
                try:
                    person_responsible_query.compliance_category_percentage = compliance_category_percentage[compliance_category_value[
                        got_value]]
                except Exception:
                    person_responsible_query.compliance_category_percentage = ''
                if got_value == 'NA':
                    person_responsible_query.remark = ''
                if (got_value and person_responsible_query.staff) or (got_value == 'NA'):
                    if len(all_person_responsible_query_of_this_checklist) > int(person_responsible_query.mystery_checklist.minimum_person_responsible):
                        person_responsible_query.mystery_checklist.audit_status = 'Completed'
                    else:
                        person_responsible_query.mystery_checklist.audit_status = 'Pending'
                if (not got_value or (not got_value == 'NA' and not person_responsible_query.staff)):
                    person_responsible_query.mystery_checklist.audit_status = 'Pending'
                person_responsible_query.mystery_checklist.save()
                person_responsible_query.save()

            if got_name == 'person_responsible':
                try:
                    got_staff = UserProfile.objects.get(
                        id=int(got_value))
                except Exception:
                    got_staff = None
                staff_name = sanitize_name(
                    got_staff.user.first_name) + ' ' + sanitize_name(got_staff.user.last_name)
                person_responsible_query.staff = got_staff
                person_responsible_query.save()
            if got_name == 'action_status':
                person_responsible_query.action_status = got_value
                person_responsible_query.save()
            if got_name == 'comment_auditor':
                person_responsible_query.comment_for_auditor = got_value
                person_responsible_query.save()
            if got_name == 'action_outlet':
                person_responsible_query.action_taken_by_outlet_manager = got_value
                person_responsible_query.save()
            if got_name == 'status_om':
                person_responsible_query.status_by_om = got_value
                person_responsible_query.save()
            if got_name == 'remark_om':
                person_responsible_query.remark_by_om = got_value
                person_responsible_query.save()
            if got_name == 'action_management':
                person_responsible_query.action_taken_by_management = got_value
                person_responsible_query.save()
            if got_name == 'remark_management':
                person_responsible_query.remark_by_management = got_value
                person_responsible_query.save()
            if got_name == 'expected_intervene':
                person_responsible_query.expected_dept_intervene = got_value
                person_responsible_query.save()
            if got_name == 'remark_department':
                person_responsible_query.remark_by_department = got_value
                person_responsible_query.save()
            if got_name == 'status_department':
                person_responsible_query.status_by_department = got_value
                person_responsible_query.save()
            ms_json = serializers.serialize('json', [person_responsible_query])
            return JsonResponse({"msg": "success", "mystery_json": json.loads(ms_json), "staff_name": staff_name})
        else:
            return JsonResponse({"msg": "failed"})
    return render(request, "mystery_shopping/mystery_shopping_tabs_page.html")


def save_user_responsible_and_kra_in_atrPage(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_resp_query_id = data['user_resp_row_id']
        got_user = data['selected_user']
        got_kra = data['get_kra']

        try:
            user_resp_query = MysteryChecklistPersonResponsible.objects.get(
                id=int(user_resp_query_id))
        except Exception:
            user_resp_query = None
        if user_resp_query:
            try:
                staff_query = UserProfile.objects.get(id=int(got_user))
            except Exception:
                staff_query = None
            user_resp_query.kra = got_kra
            user_resp_query.staff = staff_query
            user_resp_query.save()
            return JsonResponse({"msg": "success"})
        else:
            return JsonResponse({"msg": "failed"})


@csrf_exempt
def edit_mystery_file_description(request):
    if request.method == "POST":
        # data = json.loads(request.body)
        # got_query = data['data_obj']
        # print(got_query)
        got_file = request.FILES.get('file')
        file_id = request.POST.get('img_id')
        file_desc = request.POST.get('img_disc')
        audit_type = request.POST.get('audit_type')
        if audit_type == 'Mystery Shopping':
            try:
                file_query = MysteryShoppingImages.objects.get(
                    id=int(file_id))
            except Exception:
                file_query = None
        elif audit_type == 'SLR Salon':
            try:
                file_query = SlrSalonImages.objects.get(
                    id=int(file_id))
            except Exception:
                file_query = None
        if file_query:
            file_query.description = file_desc
            if got_file:
                file_query.image = got_file
            file_query.save()
        return JsonResponse({"msg": "success"})
    else:
        return JsonResponse({"msg": "failed"})


def edit_mystery_audit_status_dropdown(request):
    data = json.loads(request.body)
    got_id = data['data_id']
    got_status = data['status']
    if got_id:
        try:
            mystery_detail_query = MysteryShoppingDetail.objects.get(
                id=int(got_id))
        except Exception:
            mystery_detail_query = None

        mystery_detail_query.audit_status = got_status
        mystery_detail_query.save()
        return JsonResponse({"msg": "success"})
    else:
        return JsonResponse({"msg": "failed"})


def user_search_list(request):
    # search_query = request.GET.get('q', '')
    # if not search_query:
    #     search_query = request.GET.get('search_query', '')
    # search_query = request.GET.get('q')
    search_query = request.GET.get('search_query', '')
    print('search', search_query)
    user_query = ExtendedZenotiEmployeesData.objects.filter(
        Q(zenoti_data__employee_name__icontains=search_query))
    final_data = []
    for obj in user_query:
        temp = {}
        temp['id'] = obj.id
        temp['name'] = obj.zenoti_data.employee_name
        final_data.append(temp)
    return JsonResponse(final_data, safe=False)
# def add_service_agent_to_mystery_shopping(request, pk):
#     mystery_shopping = MysteryShoppingOverview.objects.get(id=pk)
#     mystery_detail = MysteryShoppingDetail.objects.filter(
#         mystery_shopping=mystery_shopping)
#     data_json = open("mistery_data.txt", "r")
#     mystery_detail_data = json.loads(data_json.read())
#     for overview in mystery_detail_data:
#         if overview['kra'] == 'Service Agent':
#             if overview['service_number'] == "1":
#                 service_responsible = mystery_shopping.service_agent_1
#             elif overview['service_number'] == "2":
#                 service_responsible = mystery_shopping.service_agent_2
#             elif overview['service_number'] == "3":
#                 service_responsible = mystery_shopping.service_agent_3
#             else:
#                 service_responsible = None

#             MysteryShoppingDetail.objects.create(
#                 mystery_shopping=mystery_shopping,
#                 center=mystery_shopping.center,
#                 staff=service_responsible,
#                 date=mystery_shopping.date,
#                 sequence=overview['sequence'],
#                 client_journey=overview['client_journey'],
#                 kra=overview['kra'],
#                 process=overview['process'],
#                 checklist=overview['checklist'],
#                 relative_gaps_found=overview['relative_gaps_found'],
#                 compliance_dropdown=overview['dropdown'],
#                 service_number=overview['service_number']
#             )
#             print('yes')

#     context = {}
#     return HttpResponse('Done')


def send_email_to_mystery_shopper_for_action_required(request):
    all_mystery_shopper = UserProfile.objects.filter(
        user_type_name__user_type='Mystery Shopper')
    print('all_mystery', all_mystery_shopper)
    for mystery_shopper in all_mystery_shopper:
        all_mystery_shoppping = MysteryShoppingOverview.objects.filter(
            added_by=mystery_shopper)
        all_mystery_shopping_detail = MysteryShoppingDetail.objects.filter(
            mystery_shopping__in=all_mystery_shoppping)
        all_action_required = all_mystery_shopping_detail.filter(
            audit_status='Action Required')
        if all_action_required:
            print('shopper', mystery_shopper.email)
            msg_html = render_to_string(
                'email_template/action_required_email.html',)
            text_content = strip_tags(msg_html)
            email = EmailMultiAlternatives(
                # title
                f'Bodycraft Mystery Shopping Action Required',

                # context
                text_content,

                # from email
                settings.EMAIL_HOST_USER,

                # to email
                [mystery_shopper.email],
            )
            email.attach_alternative(msg_html, "text/html")
            email.send()
    return HttpResponse('Email sent successfully')
