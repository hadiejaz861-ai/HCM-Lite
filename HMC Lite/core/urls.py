
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="core/login.html",
            redirect_authenticated_user=True,
            next_page="/",
        ),
        name="login",
    ),
    path("logout/", views.logout_user, name="logout"),
    path("", views.dashboard, name="dashboard"),

    path(
        "companies/",
        views.company_list,
        name="company_list",
    ),
    path(
        "employees/",
        views.employee_list,
        name="employee_list",
    ),
    path(
        "attendance/",
        views.attendance_page,
        name="attendance_page",
    ),
    path(
        "leaves/",
        views.leave_page,
        name="leave_page",
    ),
    path(
        "payroll/",
        views.payroll_page,
        name="payroll_page",
    ),
]

