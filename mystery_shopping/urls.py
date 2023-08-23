from django.urls import path
from .views import audit_users, mystery_shopping_overview, mystery_shopping_detail, edit_mystery_shopping_profile, edit_mystery_shopping, edit_mystery_extra_data, edit_audit_user_modal_popup, edit_mystery_audit_status_dropdown, user_search_list, edit_mystery_shopping_action_required, send_email_to_mystery_shopper_for_action_required, edit_mystery_reviewed_data, edit_mystery_file_description, mark_important_chcklist, set_center_correspondence_to_usertype
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('audit_users/', audit_users, name='audit_users'),
    path('set_center_correspondence_to_usertype/', set_center_correspondence_to_usertype,
         name='set_center_correspondence_to_usertype'),
    path('mystery_shopping/', mystery_shopping_overview,
         name='mystery_shopping'),
    path('mystery_shopping/<str:pk>/', mystery_shopping_detail,
         name='mystery_shopping_detail'),
    path('edit_mystery_shopping_profile/', edit_mystery_shopping_profile,
         name='edit_mystery_shopping_profile'),
    path('edit_mystery_shopping/', edit_mystery_shopping,
         name='edit_mystery_shopping'),
    path('edit_mystery_extra_data/', edit_mystery_extra_data,
         name='edit_mystery_extra_data'),
    path('mark_important_chcklist/', mark_important_chcklist,
         name='mark_important_chcklist'),
    path('edit_audit_user_modal_popup/', edit_audit_user_modal_popup,
         name='edit_audit_user_modal_popup'),
    path('edit_mystery_audit_status_dropdown/',
         edit_mystery_audit_status_dropdown, name='edit_mystery_audit_status_dropdown'),
    path('user_search_list/', user_search_list, name='user_search_list'),
    path('edit_mystery_shopping_action_required/', edit_mystery_shopping_action_required,
         name='edit_mystery_shopping_action_required'),
    path('send_email_to_mystery_shopper_for_action_required/',
         send_email_to_mystery_shopper_for_action_required, name='send_email_to_mystery_shopper_for_action_required'),
    path('edit_mystery_reviewed_data/', edit_mystery_reviewed_data,
         name='edit_mystery_reviewed_data'),
    path('edit_mystery_file_description/', edit_mystery_file_description,
         name='edit_mystery_file_description'),

    #     path('add_service_agent_to_mystery_shopping/<str:pk>/',
    #          add_service_agent_to_mystery_shopping, name='add_service_agent_to_mystery_shopping'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
