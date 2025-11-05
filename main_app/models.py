from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('SUPERUSER', 'HRSD Super User'),
    ('CHARITY_ADMIN', 'Charity Admin'),
    ('BENEFICIARY', 'Beneficiary'),
]

PROGRAM_STATUS_CHOICES = [
    ('ACTIVE', 'Active'),
    ('INACTIVE', 'Inactive'),
    ('CLOSED', 'Closed'),
]

APPLICATION_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('UNDER_REVIEW', 'Under Review'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
    ('WITHDRAWN', 'Withdrawn'),
]

CHARITY_TYPE_CHOICES = [
    ('HEALTH', 'Health'),
    ('EDUCATION', 'Education'),
    ('HOUSING', 'Housing'),
    ('FOOD', 'Food & Nutrition'),
    ('SOCIAL', 'Social Services'),
    ('OTHER', 'Other'),
]


class Charity(models.Model):
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50, unique=True)
    issuing_authority = models.CharField(max_length=200)
    charity_type = models.CharField(
        max_length=50, choices=CHARITY_TYPE_CHOICES, default='OTHER')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    license_certificate = models.FileField(
        upload_to='charities/licenses/', blank=True, null=True)
    admin_id_document = models.FileField(
        upload_to='charities/admin_ids/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='charity_admin', null=True, blank=True
    )

    def __str__(self):
        return self.name


class Beneficiary(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='beneficiary_profile')
    charity = models.ForeignKey(
        Charity, on_delete=models.CASCADE, related_name='beneficiaries')
    national_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    family_size = models.PositiveIntegerField(default=1)
    monthly_income = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    special_needs = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.national_id}"


class Program(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    ministry_owner = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, choices=PROGRAM_STATUS_CHOICES, default='ACTIVE')
    eligibility_criteria = models.TextField(blank=True)
    estimated_beneficiaries = models.CharField(max_length=100, blank=True)
    icon_url = models.URLField(max_length=500, blank=True)
    max_capacity = models.PositiveIntegerField(null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    charity = models.ForeignKey(
        Charity, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    max_capacity = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.charity.name}"


class EventRegistration(models.Model):
    beneficiary = models.ForeignKey(
        Beneficiary, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.beneficiary} - {self.event.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['beneficiary', 'event'], name='uniq_beneficiary_event'),
        ]


class ProgramApplication(models.Model):
    beneficiary = models.ForeignKey(
        Beneficiary, on_delete=models.CASCADE, related_name='program_applications')
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(
        max_length=20, choices=APPLICATION_STATUS_CHOICES, default='PENDING')
    application_data = models.JSONField(default=dict)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.beneficiary} - {self.program.name} - {self.status}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['beneficiary', 'program'], name='uniq_beneficiary_program'),
        ]
