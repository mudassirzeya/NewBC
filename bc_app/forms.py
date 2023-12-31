from django import forms
from .models import ExtendedZenotiEmployeesData, ExtendedZenotiCenterData, SlrAudit, UserProfile


class ExtendedUserDataForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['associated_center', 'associated_kra', 'primary_kra',
                  'associated_location', 'office_start_time',
                  'office_end_time', 'week_off', 'user_status',
                  'is_manager', 'roster_access']

        widgets = {
            'associated_center': forms.SelectMultiple(attrs={
                'class': "form-control select2",
                'multiple': "multiple",
                'style': "height: 36px;width: 100%;",
                'required': 'required',
            }),
            'associated_kra': forms.SelectMultiple(attrs={
                'class': "form-control select2",
                'multiple': "multiple",
                'style': "height: 36px;width: 100%;",
                # 'required': "required"
            }),
            'primary_kra': forms.Select(attrs={
                'class': "form-control",
                'required': "required"
            }),
            'associated_location': forms.SelectMultiple(attrs={
                'class': "form-control select2",
                'multiple': "multiple",
                'style': "height: 36px;width: 100%;",
                # 'required': "required"
            }),
            'office_start_time': forms.TimeInput(attrs={
                'class': "form-control",
                'required': "required",
                'type': 'time',
            }),
            'office_end_time': forms.TimeInput(attrs={
                'class': "form-control",
                'required': "required",
                'type': 'time',
            }),
            'week_off': forms.SelectMultiple(attrs={
                'class': "form-control select2",
                'multiple': "multiple",
                'style': "height: 36px;width: 100%;",
            }),
            'user_status': forms.Select(attrs={
                'class': "form-control",
                'required': "required",
            }),
            'is_manager': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': "pass_required(this);"
            }),
            'roster_access': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            })
        }


class ExtendedZenotiCenterDataForm(forms.ModelForm):
    class Meta:
        model = ExtendedZenotiCenterData
        fields = '__all__'
        exclude = ['zenoti_data']

        widgets = {
            'closed_on': forms.SelectMultiple(attrs={
                'class': "form-control select2",
                'multiple': "multiple",
                'style': "height: 36px;width: 100%;",
            }),
            'opening_time': forms.TimeInput(attrs={
                'class': "form-control",
                'required': "required",
                'type': 'time',
            }),
            'closing_time': forms.TimeInput(attrs={
                'class': "form-control",
                'required': "required",
                'type': 'time',
            }),
            'center_status': forms.Select(attrs={
                'class': "form-control",
                'required': 'required',
            }),
        }


class SlrAuditForm(forms.ModelForm):
    class Meta:
        model = SlrAudit
        fields = '__all__'
        exclude = ['is_deleted', 'added_on', 'added_by']

        widgets = {
            'center': forms.Select(attrs={
                'class': "form-control",
                'required': 'required',
            }),
            'access_given_to': forms.SelectMultiple(attrs={
                'class': "form-control select2",
                'multiple': "multiple",
                'style': "width: 100%;",
                'required': 'required',
            }),
            'auditor_name': forms.TextInput(attrs={
                'class': "form-control",
                'required': 'required',
            }),
            'trainer_name': forms.TextInput(attrs={
                'class': "form-control",
                'required': "required",
            }),
            'month_of_audit': forms.Select(attrs={
                'class': "form-control",
                'required': 'required',
            }),
            'date_of_audit': forms.DateInput(attrs={
                'class': "form-control ",
                'required': "required",
                'type': "date",
            }),
        }
