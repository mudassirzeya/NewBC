from django.urls import path
from .views import login_page, admin_page, logout_user, zenotiUsers_page, staff_page, employee_profile_page, edit_user_modal_popup, slr_audit_overview, slr_audit_detail, edit_slr_audit, edit_slr_salon_profile, edit_slr_salon_action_required, edit_slr_salon_extra_data, edit_slr_salon_reviewed_data, edit_slr_salon_status_dropdown, admin_zenotiCenter_page, slr_audit_access, edit_slr_access_popup, admin_team_list_page, edit_admin_modal_popup, central_access_page, edit_central_access_popup, sent_selected_user_list_to_frontend, save_selected_user_responsible, sent_all_user_list_and_compliance_to_frontend, delete_user_response, stafflist_page
urlpatterns = [
    path('user_login/', login_page, name='user_login'),
    path('user_logout/', logout_user, name='user_logout'),
    path('', admin_page, name='admin_page'),
    path('zenotiCenter_page/', admin_zenotiCenter_page,
         name='zenotiCenter_page'),
    path('zenoti_staffs_list/', zenotiUsers_page,
         name='zenoti_staffs_list'),
    path('admin_team_list_page/', admin_team_list_page,
         name='admin_team_list_page'),
    path('edit_admin_modal_popup/', edit_admin_modal_popup,
         name='edit_admin_modal_popup'),
    path('staff_lists/', stafflist_page,
         name='staff_lists'),
    path('edit_user_modal_popup/', edit_user_modal_popup,
         name='edit_user_modal_popup'),
    path('body_craft_staff_profile/<str:pk>/', employee_profile_page,
         name='body_craft_staff_profile'),
    path('central_audit_access/', central_access_page,
         name='central_audit_access'),
    path('edit_central_access_popup/', edit_central_access_popup,
         name='edit_central_access_popup'),
    path('slr_audit_access/', slr_audit_access, name='slr_audit_access'),
    path('slr_salon/', slr_audit_overview, name='slr_salon'),
    path('slr_salon/<str:pk>/',
         slr_audit_detail, name='slr_salon_profile'),
    path('edit_slr_access_popup/', edit_slr_access_popup,
         name='edit_slr_access_popup'),
    path('edit_slr_salon_audit/', edit_slr_audit, name='edit_slr_salon_audit'),
    path('edit_slr_salon_profile/', edit_slr_salon_profile,
         name='edit_slr_salon_profile'),
    path('edit_slr_salon_extra_data/', edit_slr_salon_extra_data,
         name='edit_slr_salon_extra_data'),
    path('edit_slr_salon_action_required/', edit_slr_salon_action_required,
         name='edit_slr_salon_action_required'),
    path('edit_slr_salon_status_dropdown/', edit_slr_salon_status_dropdown,
         name='edit_slr_salon_status_dropdown'),
    path('edit_slr_salon_reviewed_data/', edit_slr_salon_reviewed_data,
         name='edit_slr_salon_reviewed_data'),
    path('sent_selected_user_list_to_frontend/', sent_selected_user_list_to_frontend,
         name='sent_selected_user_list_to_frontend'),
    path('save_selected_user_responsible/', save_selected_user_responsible,
         name='save_selected_user_responsible'),
    path('sent_all_user_list_and_compliance_to_frontend/', sent_all_user_list_and_compliance_to_frontend,
         name='sent_all_user_list_and_compliance_to_frontend'),
    path('delete_user_response/', delete_user_response,
         name='delete_user_response'),
]
