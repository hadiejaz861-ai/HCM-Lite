
from django import forms
from .models import Company, Employee


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "email", "address"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter company name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter company email",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter company address",
                "rows": 3,
            }),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "company",
            "name",
            "email",
            "job_title",
            "department",
            "joining_date",
            "salary",
            "role",
            "is_active",
        ]

        widgets = {
            "company": forms.Select(attrs={
                "class": "form-control",
            }),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter employee full name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter employee email",
            }),
            "job_title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter job title",
            }),
            "department": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter department",
            }),
            "joining_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "salary": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter salary",
                "min": "0",
                "step": "0.01",
            }),
            "role": forms.Select(attrs={
                "class": "form-control",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }
