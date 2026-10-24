
from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("HR", "HR"),
        ("Employee", "Employee"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    joining_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="Employee",
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    STATUS = [
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Late", "Late"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
    )
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default="Present",
    )
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["-date"]

    def __str__(self):
        return (
            f"{self.employee.name} - "
            f"{self.date} - {self.status}"
        )


class LeaveRequest(models.Model):
    STATUS = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default="Pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.status}"


class Payroll(models.Model):
    STATUS = [
        ("Draft", "Draft"),
        ("Finalized", "Finalized"),
        ("Paid", "Paid"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
    )
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default="Draft",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("employee", "month", "year")
        ordering = ["-year", "-month"]

    @property
    def net_salary(self):
        return self.basic_salary + self.bonus - self.deductions

    def __str__(self):
        return f"{self.employee.name} - {self.month}/{self.year}"




