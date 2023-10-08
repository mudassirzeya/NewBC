from django.shortcuts import render, redirect
from .models import EmployeeRoster, EmployeeScheduler, ErrorLog
from bc_app.models import UserProfile, ExtendedZenotiCenterData, KRA, EmployeesLeaveData, Location, CenterKra
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta, datetime
import calendar
import json
import csv
# Create your views here.


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)


def handle_name_if_none(first_name, last_name):
    try:
        firstname = first_name
    except Exception:
        firstname = ''
    try:
        lastname = last_name
    except Exception:
        lastname = ''
    return firstname + ' ' + lastname


@login_required(login_url='user_login')
def roster_dashboard_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    all_centers = ExtendedZenotiCenterData.objects.filter(
        center_status='Active')
    if staffProfile.is_manager and not staffProfile.roster_access:
        this_user_centers_id = staffProfile.associated_center.all().values_list('id',
                                                                                flat=True)
        all_centers = all_centers.filter(id__in=this_user_centers_id)
    all_roster = EmployeeRoster.objects.all()
    all_locations = Location.objects.all()
    all_kra_list = KRA.objects.all()
    redirect_uri = ''
    selected_center = request.GET.get('selected_center')
    selected_date = request.GET.get('selected_date')
    selected_location = request.GET.getlist('selected_location')
    if selected_center:
        request.session['selected_center'] = selected_center
    q_date = date.today()
    if not selected_date and not selected_center and not selected_location:
        print('yes')
        if request.session.get('selected_center'):
            selected_center = request.session.get('selected_center')
        else:
            selected_center = all_centers.first().id
        # if request.session.get('selected_section'):
        #     selected_section = request.session.get('selected_section')
        # else:
        selected_location = '0'
        redirect_uri = f"/roster_dashboard/?selected_center={selected_center}&selected_location={selected_location}&selected_date={q_date}"
        return redirect(redirect_uri)
    if not selected_date:
        selected_date = q_date
    if not selected_location:
        selected_location = '0'
    try:
        searched_center = all_centers.get(id=int(selected_center))
    except Exception:
        searched_center = all_centers.first()

    try:
        searched_location = all_locations.filter(id__in=selected_location)
    except Exception:
        searched_location = all_locations.first()
    print('center', searched_center, searched_location)
    this_center_employees = UserProfile.objects.filter(
        associated_center=searched_center)
    final_employee_list = []
    for emp in this_center_employees:
        temp = {}
        temp['id'] = emp.id
        temp['name'] = emp.user.first_name + ' ' + emp.user.last_name
        temp['associated_kra'] = list(emp.associated_kra.all(
        ).values_list('id', flat=True))
        temp['associated_location'] = list(emp.associated_location.all(
        ).values_list('id', flat=True))
        final_employee_list.append(temp)

    all_roster = all_roster.filter(
        center=searched_center, appoint_date=selected_date)
    try:
        this_center_kra_with_location = CenterKra.objects.filter(
            center=searched_center)
    except Exception:
        this_center_kra_with_location = CenterKra.objects.filter(
            center=searched_center)

    if searched_location:
        this_center_kra_with_location = this_center_kra_with_location.filter(
            location__in=searched_location)

    extract_this_center_kra_list = [
        center_kra.kra for center_kra in this_center_kra_with_location]
    this_center_kra = list(set(extract_this_center_kra_list))
    if not '0' in selected_location:
        all_roster = all_roster.filter(associated_kra__in=this_center_kra)
    center_kra_json = {}
    center_kra_list = []

    # print('all_', extend_center_position_list)

    # if not '0' in selected_location:
    #     extend_center_position_list = []
    #     for each_kra in all_kra_list:
    #         if each_kra in this_center_kra:
    #             extend_center_position_list.append(each_kra)
    # else:
    #     extend_center_position_list = this_center_kra
    print('kra ', this_center_kra_with_location)
    for each_kra_location in this_center_kra_with_location:
        temp = {}
        name = each_kra_location.kra.kra + ' - ' + each_kra_location.location.location
        id = 'A'+str(each_kra_location.id)
        center_kra_json[name] = id
        temp['name'] = name
        temp['id'] = id
        center_kra_list.append(temp)
    # print('role', center_role_list)
    final_roster_list = []
    for roster in all_roster:
        temp = {}
        temp["name"] = handle_name_if_none(
            roster.employee.user.first_name, roster.employee.user.last_name)
        temp["kra"] = roster.associated_kra.kra + \
            ' - ' + roster.associated_location.location
        temp['start_time'] = str(roster.office_start_time)
        temp['end_time'] = str(roster.office_end_time)
        temp['roster_pk'] = roster.id
        final_roster_list.append(temp)

    # print('list', final_roster_list)

    all_scheduler = EmployeeScheduler.objects.filter(
        center=searched_center, appoint_date=selected_date
    ).order_by('status', 'office_start_time')

    # this is done bcs if all_scheuler will be empty in any filter with section so in frontend it wont show Create Sheduler if there is scheduler in any other section
    is_scheduler = all_scheduler.exists()

    if not '0' in selected_location:
        all_scheduler = all_scheduler.filter(
            employee__associated_kra__in=this_center_kra).distinct()
    # print('schedler', all_scheduler)
    # print('all_roster', json.dumps(final_roster_list))
    if request.method == 'POST':
        print('submit', request.POST)
        if 'create_one_roster' in request.POST:
            # print('form', roster_form.cleaned_data['employee'])
            from_time = request.POST.get("start_tm")
            to_time = request.POST.get("end_tm")
            employee_id = request.POST.get("filtered_employee")
            kra_id = request.POST.get("select_kra")
            location_id = request.POST.get("select_location")
            employee = UserProfile.objects.get(
                id=int(employee_id))
            try:
                kra_query = KRA.objects.get(id=int(kra_id))
            except Exception:
                kra_query = None
            try:
                location_query = Location.objects.get(id=int(location_id))
            except Exception:
                location_query = None
            EmployeeRoster.objects.create(
                center=searched_center,
                employee=employee,
                associated_kra=kra_query,
                associated_location=location_query,
                appoint_date=selected_date,
                office_start_time=from_time,
                office_end_time=to_time
            )
            error_sentence = f"One Roster is created for {handle_name_if_none(employee.user.first_name, employee.user.last_name)} as {kra_query.kra} for {selected_date} at {searched_center.zenoti_data.name}"
            data_sentence = f"employee: {handle_name_if_none(employee.user.first_name, employee.user.last_name)}, KRA: {kra_query.kra}. start: {employee.office_start_time}, End: {employee.office_end_time}"
            ErrorLog.objects.create(
                employee=staffProfile,
                page='roster',
                sentence=error_sentence,
                data=data_sentence
            )
        if 'copy_roster_to_future' in request.POST:
            from_date = request.POST.get("future_from")
            to_date = request.POST.get("future_to")
            # print('fut', type(from_date), to_date, del_check)
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            end_date = datetime.strptime(to_date, '%Y-%m-%d')
            all_scheduler = EmployeeScheduler.objects.filter(
                center=searched_center, appoint_date=selected_date)
            roster_log_list = []
            scheduler_log_list = []
            for single_date in daterange(start_date, end_date):
                EmployeeRoster.objects.filter(
                    center=searched_center,
                    appoint_date=single_date).delete()
                for roster in all_roster:
                    temp = {}
                    temp['employee'] = handle_name_if_none(
                        roster.employee.user.first_name, roster.employee.user.last_name)
                    temp['associated_kra'] = roster.associated_kra.kra
                    temp['associated_location'] = roster.associated_location.location
                    temp['from_time'] = roster.office_start_time
                    temp['end_time'] = roster.office_end_time
                    roster_log_list.append(temp)
                    # print('loop')
                    EmployeeRoster.objects.create(
                        center=roster.center,
                        employee=roster.employee,
                        associated_kra=roster.associated_kra,
                        associated_location=roster.associated_location,
                        appoint_date=single_date,
                        office_start_time=roster.office_start_time,
                        office_end_time=roster.office_end_time
                    )
                if all_scheduler:
                    exist_scheduler = EmployeeScheduler.objects.filter(
                        center=searched_center, appoint_date=single_date)
                    if exist_scheduler:
                        exist_scheduler.delete()
                    for scheduler in all_scheduler:
                        temp = {}
                        log_associated_kra = [
                            each_kra.kra for each_kra in scheduler.associated_kra.all()]
                        temp['associated_kra'] = log_associated_kra
                        temp['associated_location'] = scheduler.associated_location
                        temp['employee'] = handle_name_if_none(
                            scheduler.employee.user.first_name, scheduler.employee.user.last_name)
                        temp['start'] = scheduler.office_start_time
                        temp['end'] = scheduler.office_end_time
                        temp['status'] = scheduler.status
                        scheduler_log_list.append(temp)
                        each_scheduler = EmployeeScheduler.objects.create(
                            center=scheduler.center,
                            employee=scheduler.employee,
                            status=scheduler.status,
                            appoint_date=single_date,
                            associated_location=scheduler.associated_location,
                            office_start_time=scheduler.office_start_time,
                            office_end_time=scheduler.office_end_time
                        )
                        for each_kra in scheduler.associated_kra.all():
                            each_scheduler.associated_kra.add(each_kra)
            error_sentence = f"{searched_center.zenoti_data.name} Roster's of {selected_date} copied to future from {from_date} to {to_date}"
            ErrorLog.objects.create(
                employee=staffProfile,
                page='roster',
                sentence=error_sentence,
                data=roster_log_list + scheduler_log_list
            )
        if 'del_roster' in request.POST:
            del_roster_id = request.POST.get('del_id')

            try:
                roster_to_del = EmployeeRoster.objects.get(
                    id=int(del_roster_id))
            except Exception:
                roster_to_del = None
            error_sentence = f"One {handle_name_if_none(roster_to_del.employee.user.first_name, roster_to_del.employee.user.last_name)}'s Roster deleted for {roster_to_del.associated_kra.kra} on {roster.appoint_date} at {roster_to_del.center.zenoti_data.name}"
            data_sentence = f"employee: {handle_name_if_none(roster_to_del.employee.user.first_name, roster_to_del.employee.user.last_name)}, KRA: {roster_to_del.associated_kra.kra}. start: {roster_to_del.employee.office_start_time}, End: {roster_to_del.employee.office_end_time}"
            ErrorLog.objects.create(
                employee=staffProfile,
                page='roster',
                sentence=error_sentence,
                data=data_sentence
            )
            roster_to_del.delete()

        if 'edit_roster_form' in request.POST:
            from_time = request.POST.get("start_time")
            to_time = request.POST.get("end_time")
            emp_id = request.POST.get("employee_id")
            kra_id = request.POST.get("employee_kra")
            location_id = request.POST.get("employee_location")
            roster_id = request.POST.get('roster_id')

            try:
                emp_roster = EmployeeRoster.objects.get(id=int(roster_id))
            except Exception:
                emp_roster = None

            try:
                kra_query = KRA.objects.get(id=int(kra_id))
            except Exception:
                kra_query = None

            try:
                location_query = Location.objects.get(id=int(location_id))
            except Exception:
                location_query = None

            try:
                employee = UserProfile.objects.get(
                    id=int(emp_id))
            except Exception:
                employee = None

            emp_roster.employee = employee
            emp_roster.associated_kra = kra_query
            emp_roster.associated_location = location_query
            emp_roster.office_start_time = from_time
            emp_roster.office_end_time = to_time
            emp_roster.save()

            error_sentence = f"{handle_name_if_none(employee.user.first_name, employee.user.last_name)}'s Roster edited for {emp_roster.associated_kra.kra} on {emp_roster.appoint_date} at {emp_roster.center.zenoti_data.name}"

            data_sentence = f"employee: {handle_name_if_none(employee.user.first_name, employee.user.last_name)}, KRA: {kra_query.kra}. start: {from_time}, End: {to_time}"
            ErrorLog.objects.create(
                employee=staffProfile,
                page='roster',
                sentence=error_sentence,
                data=data_sentence
            )

        if 'scheduler_create' in request.POST:
            all_employee = UserProfile.objects.filter(
                associated_center=searched_center)
            sel_date = datetime.strptime(
                str(selected_date), '%Y-%m-%d')
            weekday = calendar.day_name[sel_date.weekday()]
            # print('week', weekday)
            scheduler_log_list = []
            for employe in all_employee:
                temp = {}
                try:
                    exist_scheduler = EmployeeScheduler.objects.get(
                        center=searched_center, appoint_date=selected_date, employee=employe)
                except Exception:
                    exist_scheduler = None
                try:
                    exist_roster = EmployeeRoster.objects.get(
                        center=searched_center, appoint_date=selected_date, employee=employe
                    )
                except Exception:
                    exist_roster = None
                status = 'Available'
                if exist_scheduler is None:
                    # zenoti_emp = ExtendedZenotiEmployeesData.objects.get(
                    #     id=employe.id)
                    emp_leave = EmployeesLeaveData.objects.filter(
                        user_profile=employe)
                    for leaves in emp_leave:
                        leave_from_date = datetime.strptime(
                            str(leaves.leave_from_date), '%Y-%m-%d')
                        leave_end_date = datetime.strptime(
                            str(leaves.leave_to_date), '%Y-%m-%d')
                        search_date = datetime.strptime(
                            str(selected_date), '%Y-%m-%d')
                        if search_date in daterange(leave_from_date, leave_end_date):
                            if leaves.status == 'Approved':
                                status = 'Leave Approved'
                            if leaves.status == 'Pending':
                                status = 'Leave Request'
                    if weekday in str(employe.week_off.all()):
                        status = 'Week Off'

                    # print('emp', all_employee)
                    emp_scheduler = EmployeeScheduler.objects.create(
                        center=searched_center,
                        employee=employe,
                        status=status,
                        appoint_date=selected_date,
                        office_start_time=employe.office_start_time,
                        office_end_time=employe.office_end_time
                    )
                    for kra in employe.associated_kra.all():
                        emp_scheduler.associated_kra.add(kra)
                    for location in employe.associated_location.all():
                        emp_scheduler.associated_location.add(location)
                    temp['employee'] = handle_name_if_none(
                        employe.user.first_name, employe.user.last_name)
                    log_associated_kra = [
                        this_kra.kra for this_kra in employe.associated_kra.all()]
                    log_associated_location = [
                        this_location.location for this_location in employe.associated_location.all()]
                    temp['associated_role'] = log_associated_kra
                    temp['associated_location'] = log_associated_location
                    temp['start'] = employe.office_start_time
                    temp['end'] = employe.office_end_time
                    temp['status'] = status
                    scheduler_log_list.append(temp)
                if status == 'Available':
                    if exist_roster is None:
                        for each_kra in employe.associated_kra.all():
                            for each_location in employe.associated_location.all():
                                try:
                                    center_kra = CenterKra.objects.get(
                                        kra=each_kra, location=each_location, center=searched_center)
                                except Exception:
                                    center_kra = None
                                if center_kra:
                                    EmployeeRoster.objects.create(
                                        center=searched_center,
                                        employee=employe,
                                        associated_kra=center_kra.kra,
                                        associated_location=center_kra.location,
                                        appoint_date=selected_date,
                                        office_start_time=employe.office_start_time,
                                        office_end_time=employe.office_end_time
                                    )
            error_sentence = f"The Scheduler for {searched_center.zenoti_data.name} on {selected_date} has been created."
            ErrorLog.objects.create(
                employee=staffProfile,
                page='roster',
                sentence=error_sentence,
                data=scheduler_log_list
            )

        if 'refresh_scheduler' in request.POST:
            all_employee = UserProfile.objects.filter(
                associated_center=searched_center)
            sel_date = datetime.strptime(
                str(selected_date), '%Y-%m-%d')
            weekday = calendar.day_name[sel_date.weekday()]
            try:
                # all_scheduler = EmployeeScheduler.objects.filter(
                #     center=extend_center_data, appoint_date=selected_date)
                all_scheduler = all_scheduler
            except Exception:
                all_scheduler = None

            try:
                # all_roster = EmployeeRoster.objects.filter(
                #     center=extend_center_data, appoint_date=selected_date)
                all_roster = all_roster
            except Exception:
                all_roster = None

            if all_scheduler:
                for each_scheduler in all_scheduler:
                    each_scheduler.delete()
            if all_roster:
                all_roster.delete()
            # EmployeeScheduler.objects.filter(
            #     center=extend_center_data, appoint_date=selected_date).delete()
            scheduler_log_list = []
            for each_emp in all_employee:
                temp = {}
                try:
                    exist_scheduler = EmployeeScheduler.objects.get(
                        employee=each_emp, appoint_date=selected_date,
                        center=searched_center)
                except Exception:
                    exist_scheduler = None

                try:
                    exist_roster = EmployeeRoster.objects.filter(
                        employee=each_emp, appoint_date=selected_date,
                        center=searched_center)
                except Exception:
                    exist_roster = None
                status = 'Available'
                if exist_scheduler is None:
                    print('true')
                    emp_leave = EmployeesLeaveData.objects.filter(
                        user_profile=each_emp)
                    for leaves in emp_leave:
                        leave_from_date = datetime.strptime(
                            str(leaves.leave_from_date), '%Y-%m-%d')
                        leave_end_date = datetime.strptime(
                            str(leaves.leave_to_date), '%Y-%m-%d')
                        search_date = datetime.strptime(
                            str(selected_date), '%Y-%m-%d')
                        if search_date in daterange(leave_from_date, leave_end_date):
                            if leaves.status == 'Approved':
                                print('approved')
                                status = 'Leave Approved'
                            if leaves.status == 'Pending':
                                print('pending')
                                status = 'Leave Request'
                    if weekday in str(each_emp.week_off.all()):
                        print('weekoff')
                        status = 'Week Off'

                    # print('emp', all_employee)
                    emp_scheduler = EmployeeScheduler.objects.create(
                        center=searched_center,
                        employee=each_emp,
                        status=status,
                        appoint_date=selected_date,
                        office_start_time=each_emp.office_start_time,
                        office_end_time=each_emp.office_end_time
                    )
                    for kra in each_emp.associated_kra.all():
                        emp_scheduler.associated_kra.add(kra)
                    for location in each_emp.associated_location.all():
                        emp_scheduler.associated_location.add(location)
                    temp['employee'] = handle_name_if_none(
                        each_emp.user.first_name, each_emp.user.last_name)
                    log_associated_kra = [
                        this_kra.kra for this_kra in emp_scheduler.employee.associated_kra.all()]
                    log_associated_location = [
                        this_location.location for this_location in emp_scheduler.employee.associated_location.all()]
                    temp['associated_kra'] = log_associated_kra
                    temp['associated_location'] = log_associated_location
                    temp['start'] = each_emp.office_start_time
                    temp['end'] = each_emp.office_end_time
                    temp['status'] = status
                    scheduler_log_list.append(temp)
                else:
                    leaves = EmployeesLeaveData.objects.filter(
                        zenoti_data=each_emp)
                    print(leaves)
                    for each_leave in leaves:
                        leave_from_date = datetime.strptime(
                            str(each_leave.leave_from_date), '%Y-%m-%d')
                        leave_end_date = datetime.strptime(
                            str(each_leave.leave_to_date), '%Y-%m-%d')
                        compare_date = datetime.strptime(
                            str(selected_date), '%Y-%m-%d')
                        if compare_date in daterange(leave_from_date, leave_end_date):
                            if each_leave.status == 'Approved':
                                exist_scheduler.status = 'Leave Approved'
                                exist_scheduler.save()
                            if each_leave.status == 'Pending':
                                exist_scheduler.status = 'Leave Request'
                                exist_scheduler.save()
                    # if weekday in str(each_emp.week_off.all()):
                    #     status = 'Week Off'
                    # exist_scheduler.status = status
                if status == 'Available':
                    # if exist_roster is None:
                    for each_kra in each_emp.associated_kra.all():
                        for each_location in each_emp.associated_location.all():
                            try:
                                center_kra = CenterKra.objects.get(
                                    kra=each_kra, location=each_location, center=searched_center)
                            except Exception:
                                center_kra = None
                            if center_kra:
                                EmployeeRoster.objects.create(
                                    center=searched_center,
                                    employee=each_emp,
                                    associated_kra=center_kra.kra,
                                    associated_location=center_kra.location,
                                    appoint_date=selected_date,
                                    office_start_time=each_emp.office_start_time,
                                    office_end_time=each_emp.office_end_time
                                )
            error_sentence = f"Scheduler & Roster refreshed at {searched_center.zenoti_data.name} for {selected_date}"
            ErrorLog.objects.create(
                employee=staffProfile,
                page='roster',
                sentence=error_sentence,
                data=scheduler_log_list
            )
        if 'delete_scheduler' in request.POST:
            filtered_scheduler = all_scheduler
            filtered_roster = all_roster
            scheduler_log_list = []
            for each_scheduler in filtered_scheduler:
                temp = {}
                temp['employee'] = handle_name_if_none(
                    each_scheduler.employee.user.first_name, each_scheduler.employee.user.last_name)
                log_associated_kra = [
                    this_kra.kra for this_kra in each_scheduler.employee.associated_kra.all()]
                log_associated_location = [
                    this_location.location for this_location in each_scheduler.employee.associated_location.all()]
                temp['associated_role'] = log_associated_kra
                temp['associated_location'] = log_associated_location
                temp['start'] = each_scheduler.employee.office_start_time
                temp['end'] = each_scheduler.employee.office_end_time
                temp['status'] = each_scheduler.status
                scheduler_log_list.append(temp)
            if filtered_scheduler:
                for each_scheduler in filtered_scheduler:
                    each_scheduler.delete()
            if filtered_roster:
                filtered_roster.delete()
            error_sentence = f"Scheduler & Roster deleted at {searched_center.zenoti_data.name} for {selected_date}"
            ErrorLog.objects.create(
                employee=staffProfile,
                page='roster',
                sentence=error_sentence,
                data=scheduler_log_list
            )
        selected_location_values = '&selected_location='.join(
            selected_location)
        if selected_date:
            redirect_uri = f"/roster_dashboard/?selected_center={selected_center}&selected_location={selected_location_values}&selected_date={selected_date}"
        else:
            redirect_uri = f"/roster_dashboard/?selected_center={selected_center}&selected_location={selected_location_values}&selected_date={q_date}"
        # print(selected_section_values)
        return redirect(redirect_uri)
    context = {'staffProfile': staffProfile,
               'all_centers': all_centers,
               #    'roster_form': roster_form,
               'all_roster': all_roster,
               #    'all_position': all_position,
               #    'redirect_uri': redirect_uri,
               'center_id': selected_center,
               'location_id': selected_location,
               'all_scheduler': all_scheduler,
               'is_scheduler': is_scheduler,
               'this_center_kra': this_center_kra,
               'roster_list': json.dumps(final_roster_list),
               'center_kra_list': json.dumps(center_kra_list),
               'center_kra_json': json.dumps(center_kra_json),
               'all_location': all_locations,
               'this_center_emp': final_employee_list,
               'extend_center_data': searched_center,
               'emp_json': json.dumps(final_employee_list)
               }
    return render(request, "roster/employee_roster.html", context)


def roster_missing_report(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        print("data", got_query)
        from_date = got_query[0]['from_dt']
        to_date = got_query[0]['to_dt']
        center_id = got_query[0]['center']
        location_id = got_query[0]['location']
        try:
            center_data = ExtendedZenotiCenterData.objects.get(
                id=int(center_id))
        except Exception:
            center_data = None
        try:
            location_query = Location.objects.get(id=int(location_id))
        except Exception:
            location_query = None
        all_kra = CenterKra.objects.filter(center=center_data)
        # print('position', positions)
        start_date = datetime.strptime(from_date, '%Y-%m-%d')
        end_date = datetime.strptime(to_date, '%Y-%m-%d')
        # all_role = positions
        rosters = EmployeeRoster.objects.filter(center=center_data)
        if not location_id == '0':
            all_kra = all_kra.filter(location=location_query)
            rosters = rosters.filter(associated_kra_id__in=list(
                all_kra.values_list('id', flat=True)))
        final_missing_report = []
        # print('yep')
        if start_date and end_date and center_data:
            # print('yes')
            for single_date in daterange(start_date, end_date):
                # print('single', single_date)
                for each_kra in all_kra:
                    # print('role', each_role)
                    this_kra_rosters = rosters.filter(
                        associated_kra=each_kra.kra, appoint_date=single_date, associated_location=each_kra.location
                    ).order_by('office_start_time')

                    if not this_kra_rosters:
                        final_missing_report.append(
                            '<span class="badge badge-primary" > ' + str(single_date.date()) + '</span> ' +
                            each_kra.kra.kra + '-' + each_kra.location.location + ' is not appointed whole day.'
                        )

                    endtime = None
                    # print('rosterlen', len(role_rosters))
                    for i in range(len(this_kra_rosters)):
                        each_roster = this_kra_rosters[i]
                        weekday = calendar.day_name[single_date.weekday()]
                        try:
                            this_roster_employee = UserProfile.objects.get(
                                id=each_roster.employee.id
                            )
                        except Exception:
                            this_roster_employee = None

                        if weekday in str(this_roster_employee.week_off.all()):
                            # print('yes weekoff exist')
                            final_missing_report.append(
                                '<span class="badge badge-primary" > ' + str(single_date.date()) + '</span> ' + handle_name_if_none(
                                    this_roster_employee.user.first_name, this_roster_employee.user.last_name) + ' is appointed as ' +
                                each_kra.kra.kra + '-' + each_kra.location.location + ' from ' + str(each_roster.office_start_time.strftime("%I:%M %p")) + ' to ' +
                                str(each_roster.office_end_time.strftime("%I:%M %p")) +
                                ', But the staff has Weekoff'
                            )

                        try:
                            employee_leave = EmployeesLeaveData.objects.filter(
                                user_profile=each_roster.employee)
                        except Exception:
                            employee_leave = None

                        for leave in employee_leave:
                            leave_from_date = datetime.strptime(
                                str(leave.leave_from_date), '%Y-%m-%d')
                            leave_end_date = datetime.strptime(
                                str(leave.leave_to_date), '%Y-%m-%d')
                            if single_date in daterange(leave_from_date, leave_end_date):
                                # print('type', single_date)
                                # if single_date == each_date:
                                if leave.status == 'Approved' or leave.status == 'Pending':
                                    final_missing_report.append(
                                        '<span class="badge badge-primary" > '+str(single_date.date()) + '</span> ' + handle_name_if_none(
                                            leave.user_profile.user.first_name, leave.user_profile.user.last_name) + ' is appointed as ' +
                                        each_kra.kra.kra + '-' + each_kra.location.location + ' But he is on a leave '
                                    )

                        # print('weekday', type(weekday))
                        # print('roster', each_roster)
                        if i == 0:
                            # print('loop1')
                            if each_roster.office_start_time > each_kra.kra.start_time:
                                final_missing_report.append(
                                    '<span class="badge badge-primary" > '+str(single_date.date()) + '</span> ' +
                                    each_kra.kra.kra + '-' + each_kra.location.location + ' is not appointed from '
                                    + str(each_kra.kra.start_time.strftime("%I:%M %p")) +
                                    ' to ' +
                                    str(each_roster.office_start_time.strftime(
                                        "%I:%M %p"))

                                )
                        elif i == len(this_kra_rosters)-1:
                            if each_roster.office_start_time > endtime:
                                final_missing_report.append(
                                    '<span class="badge badge-primary" > '+str(single_date.date()) + '</span> ' +
                                    each_kra.kra.kra + '-' + each_kra.location.location + ' is not appointed from '
                                    + str(endtime.strftime("%I:%M %p")) +
                                    ' to ' +
                                    str(each_roster.office_start_time.strftime(
                                        "%I:%M %p"))
                                )

                            if each_roster.office_end_time < each_kra.kra.end_time:
                                final_missing_report.append(
                                    '<span class="badge badge-primary" > '+str(single_date.date()) + '</span> ' +
                                    each_kra.kra.kra + '-' + each_kra.location.location
                                    + " is not appointed from " +
                                    str(each_roster.office_end_time.strftime("%I:%M %p")) + ' to ' +
                                    str(each_kra.kra.end_time.strftime("%I:%M %p"))

                                )
                        else:
                            # print('end', endtime)
                            if each_roster.office_start_time > endtime:
                                final_missing_report.append(
                                    '<span class="badge badge-primary" >'+str(single_date.date()) + '</span> ' +
                                    each_kra.kra.kra + '-' + each_kra.location.location
                                    + ' is not appointed from ' +
                                    str(endtime.strftime("%I:%M %p")) + ' to ' +
                                    str(each_roster.office_start_time.strftime(
                                        "%I:%M %p"))
                                )

                        endtime = each_roster.office_end_time
                        # print('time', endtime.strftime("%I:%M %p"))
        else:
            pass
        return JsonResponse({"msg": "success",
                             "roster_data": final_missing_report,
                             })
    return render(request, "employee_roster.html")


def edit_employee_scheduler(request):
    if request.method == "POST":
        user = request.user
        staffProfile = UserProfile.objects.get(user=user)
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print("data", got_query)
        start_time = got_query[0]['from_tm']
        end_time = got_query[0]['to_tm']
        status = got_query[0]['status']
        scheuler_id = got_query[0]['scheduler']
        remark = got_query[0]['remark']
        try:
            scheduler = EmployeeScheduler.objects.get(id=int(scheuler_id))
        except Exception:
            scheduler = None

        try:
            rosters = EmployeeRoster.objects.filter(
                center=scheduler.center, appoint_date=scheduler.appoint_date, employee=scheduler.employee)
        except Exception:
            rosters = None
        if scheduler:
            scheduler.office_start_time = start_time
            scheduler.office_end_time = end_time
            scheduler.status = status
            scheduler.remark = remark
            scheduler.save()

            if status == 'Available':
                if rosters:
                    for eachroster in rosters:
                        eachroster.office_start_time = scheduler.office_start_time
                        eachroster.office_end_time = scheduler.office_end_time
                        eachroster.save()
                else:
                    for each_kra in scheduler.employee.associated_kra.all():
                        for each_location in scheduler.employee.associated_location.all():
                            try:
                                center_kra = CenterKra.objects.get(
                                    kra=each_kra, location=each_location, center=scheduler.center)
                            except Exception:
                                center_kra = None
                            if center_kra:
                                EmployeeRoster.objects.create(
                                    center=scheduler.center,
                                    employee=scheduler.employee,
                                    associated_kra=center_kra.kra,
                                    associated_location=center_kra.location,
                                    appoint_date=scheduler.appoint_date,
                                    office_start_time=scheduler.office_start_time,
                                    office_end_time=scheduler.office_end_time,
                                )
            else:
                if rosters:
                    rosters.delete()

            error_sentence = f"Scheduler edited of {handle_name_if_none(scheduler.employee.user.first_name, scheduler.employee.user.last_name)} for {scheduler.appoint_date} at {scheduler.center.zenoti_data.name}"

            data_sentence = f"Employee: {handle_name_if_none(scheduler.employee.user.first_name, scheduler.employee.user.last_name)}, start: {scheduler.office_start_time}, end: {scheduler.office_end_time}, status: {scheduler.status}"
            ErrorLog.objects.create(
                employee=staffProfile,
                page='roster',
                sentence=error_sentence,
                data=data_sentence
            )
            # if status == 'Available':
            #     if rosters is None:
            #         for each_kra in scheduler.employee.associated_role.all():
            #             EmployeeRoster.objects.create(
            #                 center=scheduler.center,
            #                 employee=scheduler.employee,
            #                 associated_role=each_kra,
            #                 appoint_date=scheduler.appoint_date,
            #                 office_start_time=scheduler.employee.office_start_time,
            #                 office_end_time=scheduler.employee.office_end_time
            #             )
            # else:
            #     if rosters:
            #         rosters.delete()
            return JsonResponse({"msg": "success"})
        else:
            return JsonResponse({"msg": "failed"})
    return render(request, "employee_roster.html")


def edit_employee_roster(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        # print("data", got_query)
        try:
            roster = EmployeeRoster.objects.get(id=int(got_query))
        except Exception:
            roster = None
        roster_json = serializers.serialize('json', [roster])
        return JsonResponse({"msg": "success",
                             "roster_json": json.loads(roster_json)})
    return render(request, "employee_roster.html")


def roster_employee_filter(request):
    if request.method == "POST":
        data = json.loads(request.body)
        got_query = data['data_obj']
        position_id = got_query[0]['position']
        center_id = got_query[0]['center']
        print("data", got_query)
        try:
            position = KRA.objects.get(id=int(position_id))
        except Exception:
            position = None

        try:
            center = UserProfile.objects.get(id=int(center_id))
        except Exception:
            center = None

        try:
            extend_center = ExtendedZenotiCenterData.objects.get(
                zenoti_data=center)
        except Exception:
            extend_center = None
        print('yes')
        all_employee = EmployeesLeaveData.objects.filter(
            associated_center=extend_center, associated_role=position)
        employee_json = []
        for each_emp in all_employee:
            temp = {}
            temp['name'] = each_emp.zenoti_data.user.user.username
            temp['id'] = each_emp.id
        # print(all_employee)
        employee_json = serializers.serialize('json', employee_json)
        return JsonResponse({"msg": "success",
                             "employee_json": json.loads(employee_json)})
    return render(request, "employee_roster.html")


def download_csv(request):
    if request.method == 'POST':
        center_id = request.POST.get("center_id")
        start = request.POST.get("csv_from")
        end = request.POST.get("csv_to")
        csv_type = request.POST.get("csv_type")
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')

        try:
            center = ExtendedZenotiCenterData.objects.get(id=int(center_id))
        except Exception:
            center = None

        extend_center = ExtendedZenotiCenterData.objects.get(
            zenoti_data=center)
        rosters = EmployeeRoster.objects.filter(
            center=extend_center)
        schedulers = EmployeeScheduler.objects.filter(center=extend_center)
        if csv_type == 'roster':
            csv_headers = [
                'Date', 'Center', 'Employee', 'KRA', 'Start Time', 'End TIme'
            ]
        else:
            csv_headers = [
                'Date', 'Center', 'Employee', 'KRA', 'Start Time', 'End TIme', 'Status'
            ]

        rows = []
        if csv_type == 'roster':
            for single_date in daterange(start_date, end_date):
                filtered_roster = rosters.filter(appoint_date=single_date)
                for each_roster in filtered_roster:
                    rows.append([
                        each_roster.appoint_date,
                        each_roster.center.zenoti_data.name,
                        each_roster.employee.zenoti_data.employee_name,
                        each_roster.associated_role.name,
                        each_roster.office_start_time,
                        each_roster.office_end_time
                    ])
        else:
            for single_date in daterange(start_date, end_date):
                filtered_scheduler = schedulers.filter(
                    appoint_date=single_date)
                for each_scheduler in filtered_scheduler:
                    rows.append([
                        each_scheduler.appoint_date,
                        each_scheduler.center.zenoti_data.name,
                        each_scheduler.employee.zenoti_data.employee_name,
                        each_scheduler.associated_role.name,
                        each_scheduler.office_start_time,
                        each_scheduler.office_end_time,
                        each_scheduler.status
                    ])

        csv_response = HttpResponse(content_type='text/csv')

        if csv_type == 'roster':
            csv_response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
                'Roster_report-' + str(datetime.today().date()) + '.csv')
        else:
            csv_response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
                'Scheduler_report-' + str(datetime.today().date()) + '.csv')

        writer = csv.writer(csv_response)
        writer.writerow(csv_headers)
        writer.writerows(rows)
        print('response', csv_response)
        return csv_response
