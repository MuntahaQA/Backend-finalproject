from django.urls import path
from .views import (
    Home,
    CharitiesIndex,
    CharityDetail,
    BeneficiariesIndex,
    BeneficiaryDetail,
    ProgramsIndex,
    ProgramDetail,
    ProgramApplications,
    ProgramStatistics,
    MinistryStatistics,
    CharityStatistics,
    EventsIndex,
    EventDetail,
    EventRegistrations,
    CreateUserView,
    LoginView,
    VerifyUserView,
    UserProfileView,
    CharityRegisterView,
    MinistryRegisterView
)

urlpatterns = [
    path("", Home.as_view(), name="home"),
    # Charities urls
    path("charities/", CharitiesIndex.as_view(), name="charities-index"),
    path("charities/<int:charity_id>/", CharityDetail.as_view(), name="charity-detail"),
    # Beneficiaries urls
    path("beneficiaries/", BeneficiariesIndex.as_view(), name="beneficiaries-index"),
    path("beneficiaries/<int:beneficiary_id>/", BeneficiaryDetail.as_view(), name="beneficiary-detail"),
    # Programs urls
    path("programs/", ProgramsIndex.as_view(), name="programs-index"),
    path("programs/<int:program_id>/", ProgramDetail.as_view(), name="program-detail"),
    path("programs/<int:program_id>/applications/", ProgramApplications.as_view(), name="program-applications"),
    path("programs/<int:program_id>/statistics/", ProgramStatistics.as_view(), name="program-statistics"),
    # Ministry Statistics
    path("ministry/statistics/", MinistryStatistics.as_view(), name="ministry-statistics"),
    # Charity Statistics
    path("charity/statistics/", CharityStatistics.as_view(), name="charity-statistics"),
    # Events urls
    path("events/", EventsIndex.as_view(), name="events-index"),
    path("events/<int:event_id>/", EventDetail.as_view(), name="event-detail"),
    path("events/<int:event_id>/registrations/", EventRegistrations.as_view(), name="event-registrations"),
    path("events/<int:event_id>/registrations/<int:registration_id>/", EventRegistrations.as_view(), name="event-registration-delete"),
    # Auth urls
    path("users/signup/", CreateUserView.as_view(), name="signup"),
    path("users/login/", LoginView.as_view(), name="login"),
    path("users/token/refresh/", VerifyUserView.as_view(), name="token_refresh"),
    path("users/profile/", UserProfileView.as_view(), name="user-profile"),
    path("charities/register/", CharityRegisterView.as_view(), name="charity_register"),
    path("ministries/register/", MinistryRegisterView.as_view(), name="ministry_register"),
]
