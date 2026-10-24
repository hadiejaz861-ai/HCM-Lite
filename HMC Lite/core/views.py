
from datetime import date
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone

from .models import (
    Company,
    Employee,
    Attendance,
    LeaveRequest,
    Payroll,
)
from .forms import CompanyForm, EmployeeForm


def get_employee(request):
    return Employee.objects.filter(user=request.user).first()


def is_hr_or_admin(request):
    employee = get_employee(request)
    return request.user.is_superuser or (
        employee is not None and employee.role in ["Admin", "HR"]
    )


@login_required(login_url="/login/")
def dashboard(request):
    employee = get_employee(request)

    if request.user.is_superuser:
        role = "Admin"
    elif employee:
        role = employee.role
    else:
        messages.error(
            request,
            "Your account is not linked to an employee profile."
        )
        return render(
            request,
            "core/dashboard.html",
            {
                "role": "Unassigned",
                "company_count": 0,
                "employee_count": 0,
                "active_count": 0,
                "attendance_count": 0,
                "pending_leaves": 0,
                "approved_leaves": 0,
                "payroll_count": 0,
                "recent_leaves": [],
            },
        )

    if role in ["Admin", "HR"]:
        context = {
            "role": role,
            "company_count": Company.objects.count(),
            "employee_count": Employee.objects.count(),
            "active_count": Employee.objects.filter(is_active=True).count(),
            "attendance_count": Attendance.objects.count(),
            "pending_leaves": LeaveRequest.objects.filter(
                status="Pending"
            ).count(),
            "approved_leaves": LeaveRequest.objects.filter(
                status="Approved"
            ).count(),
            "payroll_count": Payroll.objects.count(),
            "recent_leaves": LeaveRequest.objects.order_by(
                "-created_at"
            )[:5],
        }
    else:
        context = {
            "role": role,
            "company_count": int(employee.company_id is not None),
            "employee_count": 1,
            "active_count": int(employee.is_active),
            "attendance_count": Attendance.objects.filter(
                employee=employee
            ).count(),
            "pending_leaves": LeaveRequest.objects.filter(
                employee=employee, status="Pending"
            ).count(),
            "approved_leaves": LeaveRequest.objects.filter(
                employee=employee, status="Approved"
            ).count(),
            "payroll_count": Payroll.objects.filter(
                employee=employee
            ).count(),
            "recent_leaves": LeaveRequest.objects.filter(
                employee=employee
            ).order_by("-created_at")[:5],
        }

    return render(request, "core/dashboard.html", context)


@login_required(login_url="/login/")
def company_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Only an Admin can manage companies.")
        return redirect("dashboard")

    companies = Company.objects.all().order_by("name")

    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Company added successfully.")
            return redirect("company_list")
    else:
        form = CompanyForm()

    return render(
        request,
        "core/companies.html",
        {"form": form, "companies": companies},
    )


@login_required(login_url="/login/")
def logout_user(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return redirect("dashboard")


@login_required(login_url="/login/")
def employee_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Only an Admin can manage employees.")
        return redirect("dashboard")

    employees = Employee.objects.select_related(
        "company"
    ).order_by("name")

    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee added successfully.")
            return redirect("employee_list")
    else:
        form = EmployeeForm()

    return render(
        request,
        "core/employees.html",
        {"form": form, "employees": employees},
    )


@login_required(login_url="/login/")
def attendance_page(request):
    if not request.user.is_superuser:
        messages.error(
            request,
            "Only an Admin can manage attendance right now."
        )
        return redirect("dashboard")

    today = timezone.localdate()
    employees = Employee.objects.filter(
        is_active=True
    ).order_by("name")

    if request.method == "POST":
        employee = employees.filter(
            id=request.POST.get("employee_id")
        ).first()
        action = request.POST.get("action")

        if not employee:
            messages.error(request, "Please select a valid employee.")
            return redirect("attendance_page")

        record, _ = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={"status": "Present"},
        )
        current_time = timezone.localtime().time().replace(
            microsecond=0
        )

        if action == "check_in":
            if record.check_in:
                messages.error(request, "Employee already checked in.")
            else:
                record.check_in = current_time
                record.status = "Present"
                record.save()
                messages.success(
                    request, f"Check-in saved for {employee.name}."
                )
        elif action == "check_out":
            if not record.check_in:
                messages.error(
                    request, "Employee must check in first."
                )
            elif record.check_out:
                messages.error(request, "Employee already checked out.")
            else:
                record.check_out = current_time
                record.save()
                messages.success(
                    request, f"Check-out saved for {employee.name}."
                )
        else:
            messages.error(request, "Invalid attendance action.")

        return redirect("attendance_page")

    records = Attendance.objects.filter(
        date=today
    ).select_related("employee").order_by("employee__name")

    return render(
        request,
        "core/attendance.html",
        {"employees": employees, "records": records, "today": today},
    )


@login_required(login_url="/login/")
def leave_page(request):
    employee = get_employee(request)
    manager = is_hr_or_admin(request)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "submit_leave":
            if not employee or employee.role != "Employee":
                messages.error(
                    request,
                    "A linked Employee account is required to apply for leave."
                )
                return redirect("leave_page")

            try:
                start_date = date.fromisoformat(
                    request.POST.get("start_date", "")
                )
                end_date = date.fromisoformat(
                    request.POST.get("end_date", "")
                )
                reason = request.POST.get("reason", "").strip()

                if end_date < start_date:
                    raise ValueError("End date cannot be before start date.")
                if not reason:
                    raise ValueError("Please enter a reason.")

                LeaveRequest.objects.create(
                    employee=employee,
                    start_date=start_date,
                    end_date=end_date,
                    reason=reason,
                )
                messages.success(request, "Leave request submitted.")
            except (ValueError, TypeError):
                messages.error(
                    request,
                    "Please enter valid dates and a reason."
                )

            return redirect("leave_page")

        if action == "update_leave":
            if not manager:
                messages.error(
                    request, "Only Admin or HR can review leave requests."
                )
                return redirect("leave_page")

            leave_id = request.POST.get("leave_id")
            new_status = request.POST.get("status")

            if new_status not in ["Approved", "Rejected"]:
                messages.error(request, "Invalid leave status.")
            else:
                leave = LeaveRequest.objects.filter(
                    id=leave_id
                ).first()

                if not leave:
                    messages.error(request, "Leave request not found.")
                elif leave.status != "Pending":
                    messages.error(
                        request, "This leave request has already been reviewed."
                    )
                else:
                    leave.status = new_status
                    leave.save(update_fields=["status"])
                    messages.success(
                        request, f"Leave request {new_status.lower()}."
                    )

            return redirect("leave_page")

    if manager:
        leaves = LeaveRequest.objects.select_related(
            "employee"
        ).order_by("-created_at")
    elif employee:
        leaves = LeaveRequest.objects.filter(
            employee=employee
        ).order_by("-created_at")
    else:
        leaves = LeaveRequest.objects.none()

    return render(
        request,
        "core/leaves.html",
        {
            "employee": employee,
            "manager": manager,
            "leaves": leaves,
        },
    )


@login_required(login_url="/login/")
def payroll_page(request):
    if not is_hr_or_admin(request):
        messages.error(
            request, "Only Admin or HR can access payroll."
        )
        return redirect("dashboard")

    employees = Employee.objects.filter(
        is_active=True
    ).order_by("name")

    if request.method == "POST":
        try:
            employee = employees.filter(
                id=request.POST.get("employee_id")
            ).first()

            if not employee:
                raise ValueError("Please select a valid employee.")

            month = int(request.POST.get("month", ""))
            year = int(request.POST.get("year", ""))

            if not 1 <= month <= 12 or not 2000 <= year <= 2100:
                raise ValueError("Enter a valid month and year.")

            bonus = Decimal(request.POST.get("bonus") or "0")
            deductions = Decimal(request.POST.get("deductions") or "0")

            if not bonus.is_finite() or not deductions.is_finite():
                raise ValueError("Invalid bonus or deductions.")
            if bonus < 0 or deductions < 0:
                raise ValueError("Bonus and deductions cannot be negative.")

            basic_salary = employee.salary

            if deductions > basic_salary + bonus:
                raise ValueError(
                    "Deductions cannot exceed salary plus bonus."
                )

            payroll, created = Payroll.objects.get_or_create(
                employee=employee,
                month=month,
                year=year,
                defaults={
                    "basic_salary": basic_salary,
                    "bonus": bonus,
                    "deductions": deductions,
                    "status": "Draft",
                },
            )

            if created:
                messages.success(
                    request,
                    f"Payroll created. Net salary: {payroll.net_salary}"
                )
            else:
                messages.error(
                    request,
                    "Payroll already exists for this employee and month."
                )

        except (ValueError, TypeError, InvalidOperation):
            messages.error(
                request,
                "Invalid payroll details. Please check all fields."
            )

        return redirect("payroll_page")

    payrolls = Payroll.objects.select_related(
        "employee"
    ).order_by("-year", "-month", "employee__name")

    return render(
        request,
        "core/payroll.html",
        {"employees": employees, "payrolls": payrolls},
    )




