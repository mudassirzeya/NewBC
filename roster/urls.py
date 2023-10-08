from django.urls import path
from .views import roster_dashboard_page, roster_missing_report, edit_employee_scheduler, edit_employee_roster, roster_employee_filter, download_csv
urlpatterns = [
    path('roster_dashboard/', roster_dashboard_page,
         name='roster_dashboard'),
    path('roster_employee_filter/', roster_employee_filter,
         name='roster_employee_filter'),
    path('edit_employee_roster/', edit_employee_roster,
         name='edit_employee_roster'),
    path('get_missing_report/', roster_missing_report, name='get_missing_report'),
    path('edit_employee_scheduler/', edit_employee_scheduler,
         name='edit_employee_scheduler'),
    path('download_csv/', download_csv, name='download_csv'),

]
