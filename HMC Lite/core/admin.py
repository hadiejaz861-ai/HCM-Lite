
from django.contrib import admin
from .models import Company, Employee, Attendance, LeaveRequest, Payroll


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "name", "email", "job_title",
        "department", "role", "joining_date",
        "salary", "is_active"
    )
    search_fields = ("name", "email", "job_title")
    list_filter = ("department", "role", "is_active")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "status")
    list_filter = ("date", "status")
    search_fields = ("employee__name",)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee", "start_date", "end_date", "status"
    )
    list_filter = ("status",)
    list_editable = ("status",)
    search_fields = ("employee__name",)


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = (
        "employee", "month", "year",
        "basic_salary", "bonus", "deductions", "status"
    )
    list_filter = ("year", "month", "status")
    list_editable = ("status",)
    search_fields = ("employee__name",)
