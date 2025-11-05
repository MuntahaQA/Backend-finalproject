

# ===== IMPORTS & HELPERS =====
from datetime import timedelta
import csv

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.db.models import Count
from django.utils import timezone
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Charity, Beneficiary, Program, Event, EventRegistration, ProgramApplication
from .serializers import (
    CharitySerializer, BeneficiarySerializer, ProgramSerializer, EventSerializer,
    EventRegistrationSerializer, ProgramApplicationSerializer, UserSerializer
)


def parse_date(value):
    if not value:
        return None
    try:
        return timezone.datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


def err(message, http=status.HTTP_400_BAD_REQUEST):
    return Response({"error": message}, status=http)


def is_ministry(user): 
    return bool(user and user.is_authenticated and user.is_superuser)


def ministry_name(user):
    return user.first_name if getattr(user, "first_name", None) else None


# ===== HOME =====
class Home(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the sila api home route!"})


# ===== CHARITIES =====
class CharitiesIndex(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CharitySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Charity.objects.all()
        if hasattr(user, "charity_admin"):
            return Charity.objects.filter(admin_user=user)
        return Charity.objects.none()

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return err("Only superusers can create charities", status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


class CharityDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CharitySerializer
    lookup_field = "id"
    lookup_url_kwarg = "charity_id"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Charity.objects.all()
        if hasattr(user, "charity_admin"):
            return Charity.objects.filter(admin_user=user)
        return Charity.objects.none()

    def get_object(self):
        charity = super().get_object()
        user = self.request.user
        if not user.is_superuser and not (hasattr(user, "charity_admin") and user.charity_admin == charity):
            raise PermissionDenied(
                "You don't have permission to view this charity")
        return charity

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return err("Only superusers can update charities", status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return err("Only superusers can delete charities", status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# ===== BENEFICIARIES =====
class BeneficiariesIndex(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BeneficiarySerializer

    def get_queryset(self):
        user = self.request.user
        qs = Beneficiary.objects.select_related("user", "charity")
        if user.is_superuser:
            return qs
        if hasattr(user, "charity_admin"):
            return qs.filter(charity=user.charity_admin)
        if hasattr(user, "beneficiary_profile"):
            return qs.filter(user=user)
        return qs.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_superuser or hasattr(user, "charity_admin")):
            return err("Only charity admins can create beneficiaries", status.HTTP_403_FORBIDDEN)

        charity = getattr(user, "charity_admin", None)
        if user.is_superuser and not charity:
            charity_id = request.data.get("charity")
            if charity_id:
                charity = get_object_or_404(Charity, id=charity_id)
        if not charity:
            return err("Charity is required")

        user_data = request.data.get("user") or {}
        email, password = user_data.get("email"), user_data.get("password")
        if not email:
            return err("Email is required")
        if not password:
            return err("Password is required")
        if User.objects.filter(email=email).exists():
            return err("Email already exists")

        base_username = user_data.get("username") or email.split("@")[0]
        username, counter = base_username, 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            if counter > 1000:
                return err("Could not generate unique username")

        national_id = request.data.get("national_id")
        if not national_id:
            return err("National ID is required")
        if Beneficiary.objects.filter(national_id=national_id).exists():
            return err("National ID already exists")

        created_user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=user_data.get("first_name", ""), last_name=user_data.get("last_name", "")
        )

        payload = request.data.copy()
        payload["user"], payload["charity"] = created_user.id, charity.id
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=created_user, charity=charity)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BeneficiaryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BeneficiarySerializer
    lookup_field = "id"
    lookup_url_kwarg = "beneficiary_id"

    def get_queryset(self):
        user = self.request.user
        qs = Beneficiary.objects.select_related("user", "charity")
        if user.is_superuser:
            return qs
        if hasattr(user, "charity_admin"):
            return qs.filter(charity=user.charity_admin)
        if hasattr(user, "beneficiary_profile"):
            return qs.filter(user=user)
        return qs.none()

    def get_object(self):
        beneficiary = super().get_object()
        user = self.request.user
        if not user.is_superuser and not (hasattr(user, "charity_admin") and user.charity_admin == beneficiary.charity):
            if beneficiary.user != user:
                raise PermissionDenied("You can only view your own profile")
        return beneficiary

    def update(self, request, *args, **kwargs):
        beneficiary = self.get_object()
        user = request.user
        if not user.is_superuser and not (hasattr(user, "charity_admin") and user.charity_admin == beneficiary.charity):
            if beneficiary.user != user:
                return err("You can only update your own profile", status.HTTP_403_FORBIDDEN)

        payload = request.data.copy()
        payload["charity"] = beneficiary.charity.id
        user_data = request.data.get("user") or {}
        if user_data and (user.is_superuser or (hasattr(user, "charity_admin") and user.charity_admin == beneficiary.charity)):
            beneficiary.user.first_name = user_data.get(
                "first_name", beneficiary.user.first_name)
            beneficiary.user.last_name = user_data.get(
                "last_name", beneficiary.user.last_name)
            beneficiary.user.save()

        serializer = self.get_serializer(beneficiary, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        beneficiary = self.get_object()
        if not request.user.is_superuser and not (hasattr(request.user, "charity_admin") and request.user.charity_admin == beneficiary.charity):
            return err("You don't have permission to delete this beneficiary", status.HTTP_403_FORBIDDEN)
        beneficiary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===== PROGRAMS =====
class ProgramsIndex(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProgramSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Program.objects.all()
        if user.is_authenticated and user.is_superuser:
            name = ministry_name(user)
            return qs.filter(ministry_owner__icontains=name) if name else qs
        return qs.filter(status="ACTIVE")

    def create(self, request, *args, **kwargs):
        if not is_ministry(request.user):
            return err("Only ministry users can create programs", status.HTTP_403_FORBIDDEN)
        name = ministry_name(request.user)
        if not name:
            return err("Ministry name not found. Please update your profile.")
        payload = request.data.copy()
        payload["ministry_owner"] = name
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProgramDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProgramSerializer
    lookup_field = "id"
    lookup_url_kwarg = "program_id"
    queryset = Program.objects.all()

    def get_object(self):
        program = super().get_object()
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            name = ministry_name(user)
            if name and program.ministry_owner and name.lower() not in program.ministry_owner.lower():
                raise PermissionDenied(
                    "You don't have permission to access this program")
        elif program.status != "ACTIVE":
            raise NotFound("Program not found")
        return program

    def update(self, request, *args, **kwargs):
        if not is_ministry(request.user):
            return err("Only ministry users can update programs", status.HTTP_403_FORBIDDEN)
        program = self.get_object()
        name = ministry_name(request.user)
        if name and program.ministry_owner and name.lower() not in program.ministry_owner.lower():
            return err("You can only update programs that belong to your ministry", status.HTTP_403_FORBIDDEN)
        payload = request.data.copy()
        if name:
            payload["ministry_owner"] = name
        serializer = self.get_serializer(program, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if not is_ministry(request.user):
            return err("Only ministry users can delete programs", status.HTTP_403_FORBIDDEN)
        program = self.get_object()
        name = ministry_name(request.user)
        if name and program.ministry_owner and name.lower() not in program.ministry_owner.lower():
            return err("You can only delete programs that belong to your ministry", status.HTTP_403_FORBIDDEN)
        program.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProgramApplications(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProgramApplicationSerializer

    def get(self, request, program_id):
        try:
            user = request.user
            if user.is_superuser:
                qs = ProgramApplication.objects.filter(program_id=program_id)
            elif hasattr(user, "charity_admin"):
                qs = ProgramApplication.objects.filter(
                    program_id=program_id, beneficiary__charity=user.charity_admin)
            elif hasattr(user, "beneficiary_profile"):
                qs = ProgramApplication.objects.filter(
                    program_id=program_id, beneficiary__user=user)
            else:
                qs = ProgramApplication.objects.none()
            return Response(self.serializer_class(qs, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            return err(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, program_id):
        try:
            if not hasattr(request.user, "beneficiary_profile"):
                return err("Only beneficiaries can apply to programs", status.HTTP_403_FORBIDDEN)
            program = get_object_or_404(Program, id=program_id)
            beneficiary = request.user.beneficiary_profile
            if ProgramApplication.objects.filter(beneficiary=beneficiary, program=program).exists():
                return err("You have already applied to this program")
            payload = {**request.data, "program": program_id,
                       "beneficiary": beneficiary.id}
            serializer = self.serializer_class(data=payload)
            serializer.is_valid(raise_exception=True)
            try:
                serializer.save()
            except IntegrityError:
                return err("You have already applied to this program")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return err(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== EVENTS =====
class EventsIndex(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EventSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Event.objects.select_related("charity")
        if user.is_authenticated:
            if user.is_superuser:
                return qs.all()
            if hasattr(user, "charity_admin"):
                return qs.filter(charity=user.charity_admin)
            if hasattr(user, "beneficiary_profile"):
                return qs.filter(charity=user.beneficiary_profile.charity, is_active=True)
        return qs.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_authenticated and (user.is_superuser or hasattr(user, "charity_admin"))):
            return err("Only superusers and charity admins can create events", status.HTTP_403_FORBIDDEN)
        payload = request.data.copy()
        if hasattr(user, "charity_admin"):
            payload["charity"] = user.charity_admin.id
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventSerializer
    lookup_field = "id"
    lookup_url_kwarg = "event_id"
    queryset = Event.objects.all()

    def update(self, request, *args, **kwargs):
        event = self.get_object()
        user = request.user
        if not (user.is_superuser or (hasattr(user, "charity_admin") and user.charity_admin == event.charity)):
            return err("You don't have permission to update this event", status.HTTP_403_FORBIDDEN)
        payload = request.data.copy()
        payload["charity"] = event.charity.id
        serializer = self.get_serializer(event, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        user = request.user
        if not (user.is_superuser or (hasattr(user, "charity_admin") and user.charity_admin == event.charity)):
            return err("You don't have permission to delete this event", status.HTTP_403_FORBIDDEN)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventRegistrations(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventRegistrationSerializer

    def get(self, request, event_id):
        try:
            user = request.user
            if user.is_superuser:
                queryset = EventRegistration.objects.filter(event_id=event_id)
            elif hasattr(user, "charity_admin"):
                queryset = EventRegistration.objects.filter(
                    event_id=event_id, event__charity=user.charity_admin)
            elif hasattr(user, "beneficiary_profile"):
                queryset = EventRegistration.objects.filter(
                    event_id=event_id, beneficiary__user=user)
            else:
                queryset = EventRegistration.objects.none()
            return Response(self.serializer_class(queryset, many=True).data, status=status.HTTP_200_OK)
        except Exception as error:
            return err(str(error), status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, event_id):
        try:
            if not hasattr(request.user, "beneficiary_profile"):
                return err("Only beneficiaries can register for events", status.HTTP_403_FORBIDDEN)

            event = get_object_or_404(Event, id=event_id)
            beneficiary = request.user.beneficiary_profile

            if EventRegistration.objects.filter(beneficiary=beneficiary, event=event).exists():
                return err("You are already registered for this event")

            current = EventRegistration.objects.filter(event=event).count()
            if event.max_capacity is not None and current >= event.max_capacity:
                return err("Event is full")

            payload = {**request.data, "event": event_id,
                       "beneficiary": beneficiary.id}
            serializer = self.serializer_class(data=payload)
            serializer.is_valid(raise_exception=True)
            try:
                instance = serializer.save()
            except IntegrityError:
                return err("You are already registered for this event")

            return Response(self.serializer_class(instance).data, status=status.HTTP_201_CREATED)
        except Exception as error:
            return err(str(error), status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, event_id, registration_id):
        try:
            registration = EventRegistration.objects.filter(id=registration_id, event_id=event_id)\
                                                    .select_related("beneficiary", "beneficiary__user").first()
            if not registration:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

            user = request.user
            if not (user.is_superuser or registration.beneficiary.user == user):
                return err("You don't have permission to delete this registration", status.HTTP_403_FORBIDDEN)

            registration.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return err(str(error), status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== AUTH =====
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data["username"],
            email=serializer.validated_data.get("email", ""),
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
        )
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        user_data["charity_admin"] = {"id": user.charity_admin.id, "name": user.charity_admin.name} if hasattr(
            user, "charity_admin") else None
        return Response({"refresh": str(refresh), "access": str(refresh.access_token), "user": user_data}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        email, password = request.data.get(
            "email"), request.data.get("password")
        if not email or not password:
            return err("Email and password are required", status.HTTP_400_BAD_REQUEST)
        try:
            found = User.objects.get(email=email)
        except User.DoesNotExist:
            return err("Invalid credentials", status.HTTP_401_UNAUTHORIZED)
        user = authenticate(username=found.username, password=password)
        if not user:
            return err("Invalid credentials", status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        user_data["charity_admin"] = {"id": user.charity_admin.id, "name": user.charity_admin.name} if hasattr(
            user, "charity_admin") else None
        return Response({"refresh": str(refresh), "access": str(refresh.access_token), "user": user_data}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        data = self.serializer_class(request.user).data
        data["charity_admin"] = {"id": request.user.charity_admin.id, "name": request.user.charity_admin.name} if hasattr(
            request.user, "charity_admin") else None
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        try:
            user = request.user
            old_first_name = user.first_name

            charity_name_update = request.data.get("charity_name")
            if charity_name_update and hasattr(user, "charity_admin"):
                charity = user.charity_admin
                charity.name = charity_name_update
                charity.save()

            serializer = self.serializer_class(
                user, data=request.data, partial=True)
            if serializer.is_valid():
                if request.data.get("password"):
                    user.set_password(request.data["password"])
                    user.save()
                    validated = serializer.validated_data.copy()
                    validated.pop("password", None)
                    validated.pop("charity_name", None)
                    serializer.save(**validated)
                else:
                    validated = serializer.validated_data.copy()
                    validated.pop("charity_name", None)
                    serializer.save(**validated)

                if user.is_superuser and "first_name" in request.data:
                    new_first_name = request.data["first_name"]
                    if old_first_name and new_first_name and old_first_name != new_first_name:
                        Program.objects.filter(ministry_owner__icontains=old_first_name).update(
                            ministry_owner=new_first_name)

                data = self.serializer_class(user).data
                data["charity_admin"] = {"id": user.charity_admin.id, "name": user.charity_admin.name} if hasattr(
                    user, "charity_admin") else None
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return err(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        refresh = RefreshToken.for_user(user)
        data = UserSerializer(user).data
        data["charity_admin"] = {"id": user.charity_admin.id, "name": user.charity_admin.name} if hasattr(
            user, "charity_admin") else None
        return Response({"refresh": str(refresh), "access": str(refresh.access_token), "user": data}, status=status.HTTP_200_OK)


class CharityRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            d = request.data
            required = [
                "admin_name", "email", "password", "phone", "organization_name", "registration_number",
                "issuing_authority", "charity_type", "address", "license_certificate", "admin_id_document"
            ]
            for f in required:
                if not d.get(f):
                    return err(f"{f} is required.")
            if User.objects.filter(email=d["email"]).exists():
                return err("Email already exists.")
            if Charity.objects.filter(registration_number=d["registration_number"]).exists():
                return err("Registration number already exists.")

            parts = d["admin_name"].strip().split(maxsplit=1)
            first_name, last_name = (
                parts[0] if parts else ""), (parts[1] if len(parts) > 1 else "")

            base = d["email"].split("@")[0]
            username = base
            i = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{i}"
                i += 1

            user = User.objects.create_user(
                username=username, email=d["email"], password=d["password"],
                first_name=first_name, last_name=last_name
            )
            charity = Charity.objects.create(
                name=d["organization_name"], registration_number=d["registration_number"],
                issuing_authority=d["issuing_authority"], charity_type=d["charity_type"],
                email=d["email"], phone=d["phone"], address=d["address"], city="", region="",
                license_certificate=d.get("license_certificate"), admin_id_document=d.get("admin_id_document"),
                admin_user=user, is_active=False,
            )
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            user_data["charity_admin"] = {
                "id": charity.id, "name": charity.name}
            return Response({"refresh": str(refresh), "access": str(refresh.access_token), "user": user_data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return err(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class MinistryRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            d = request.data
            required = [
                "responsible_person_name", "position", "ministry_email", "password",
                "contact_number", "ministry_name", "ministry_code", "authorization_document"
            ]
            for f in required:
                if not d.get(f):
                    return err(f"{f} is required.")
            if User.objects.filter(email=d["ministry_email"]).exists():
                return err("Email already exists.")

            parts = d["responsible_person_name"].strip().split(maxsplit=1)
            last_name = parts[1] if len(parts) > 1 else ""

            base = d["ministry_email"].split("@")[0]
            username = base
            i = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{i}"
                i += 1

            user = User.objects.create_user(
                username=username, email=d["ministry_email"], password=d["password"],
                first_name=d["ministry_name"], last_name=last_name, is_staff=True, is_superuser=True
            )
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            user_data["charity_admin"] = None
            return Response({"refresh": str(refresh), "access": str(refresh.access_token), "user": user_data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return err(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== STATISTICS =====
class MinistryStatistics(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            if not is_ministry(request.user):
                return err("Only ministry users can view ministry statistics", status.HTTP_403_FORBIDDEN)
            name = ministry_name(request.user)
            if not name:
                return err("Ministry name not found")
            programs = Program.objects.filter(ministry_owner__icontains=name)

            program_id = request.query_params.get("program_id")
            status_filter = request.query_params.get("status")
            date_from = parse_date(request.query_params.get("date_from"))
            date_to = parse_date(request.query_params.get("date_to"))
            if program_id:
                programs = programs.filter(id=program_id)

            apps = ProgramApplication.objects.filter(program__in=programs)
            if status_filter:
                apps = apps.filter(status=status_filter)
            if date_from:
                apps = apps.filter(submitted_at__date__gte=date_from)
            if date_to:
                apps = apps.filter(submitted_at__date__lte=date_to)

            statistics = {
                "ministry_name": name,
                "total_programs": programs.count(),
                "active_programs": programs.filter(status="ACTIVE").count(),
                "inactive_programs": programs.filter(status="INACTIVE").count(),
                "closed_programs": programs.filter(status="CLOSED").count(),
                "total_applications": apps.count(),
                "unique_beneficiaries": apps.values("beneficiary").distinct().count(),
                "applications_by_status": list(apps.values("status").annotate(count=Count("id")).order_by("status")),
                "programs_summary": [
                    {
                        "id": p.id, "name": p.name, "status": p.status,
                        "total_applications": apps.filter(program=p).count(),
                        "unique_beneficiaries": apps.filter(program=p).values("beneficiary").distinct().count(),
                    } for p in programs
                ],
                "applications_by_program": list(
                    apps.values("program__id", "program__name").annotate(
                        count=Count("id")).order_by("-count")
                ),
                "applications_over_time": [
                    {
                        "date": (timezone.now().date() - timedelta(days=29-i)).strftime("%Y-%m-%d"),
                        "day": (timezone.now().date() - timedelta(days=29-i)).strftime("%d/%m"),
                        "count": apps.filter(submitted_at__date=(timezone.now().date() - timedelta(days=29-i))).count()
                    } for i in range(30)
                ],
                "applications_by_charity": list(
                    apps.values("beneficiary__charity__id",
                                "beneficiary__charity__name")
                    .annotate(count=Count("id")).order_by("-count")[:10]
                ),
                "recent_applications": apps.filter(submitted_at__gte=timezone.now()-timedelta(days=7)).count(),
                "avg_processing_days": (lambda rows: round(sum(rows)/len(rows), 1) if rows else None)(
                    [(a.reviewed_at - a.submitted_at).days for a in apps.exclude(reviewed_at__isnull=True)
                     if a.submitted_at and a.reviewed_at]
                ),
                "filters_applied": {
                    "program_id": program_id, "status": status_filter,
                    "date_from": request.query_params.get("date_from"),
                    "date_to": request.query_params.get("date_to"),
                }
            }
            return Response(statistics, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return err(str(e), status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return err(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if not is_ministry(request.user):
                return err("Only ministry users can export statistics", status.HTTP_403_FORBIDDEN)
            name = ministry_name(request.user)
            if not name:
                return err("Ministry name not found")

            program_id = request.data.get("program_id")
            status_filter = request.data.get("status")
            date_from = parse_date(request.data.get("date_from"))
            date_to = parse_date(request.data.get("date_to"))
            export_type = request.data.get("export_type", "applications")

            programs = Program.objects.filter(ministry_owner__icontains=name)
            if program_id:
                programs = programs.filter(id=program_id)

            apps = ProgramApplication.objects.filter(program__in=programs)\
                .select_related("program", "beneficiary", "beneficiary__charity", "beneficiary__user")
            if status_filter:
                apps = apps.filter(status=status_filter)
            if date_from:
                apps = apps.filter(submitted_at__date__gte=date_from)
            if date_to:
                apps = apps.filter(submitted_at__date__lte=date_to)

            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="ministry_statistics_{name.replace(" ", "_")}_{timezone.now().strftime("%Y%m%d")}.csv"'
            )
            writer = csv.writer(response)

            if export_type == "applications":
                writer.writerow(["Application ID", "Program Name", "Program Status", "Beneficiary Name",
                                "Charity Name", "Application Status", "Submitted Date", "Reviewed Date", "Review Notes"])
                for a in apps:
                    beneficiary_name = f"{a.beneficiary.user.first_name} {a.beneficiary.user.last_name}".strip(
                    ) if a.beneficiary and a.beneficiary.user else ""
                    charity_name = a.beneficiary.charity.name if a.beneficiary and a.beneficiary.charity else ""
                    writer.writerow([
                        a.id, a.program.name, a.program.status, beneficiary_name, charity_name, a.status,
                        a.submitted_at.strftime(
                            "%Y-%m-%d %H:%M:%S") if a.submitted_at else "",
                        a.reviewed_at.strftime(
                            "%Y-%m-%d %H:%M:%S") if a.reviewed_at else "",
                        (a.review_notes or "")[:100]
                    ])
            else:
                writer.writerow(["Statistic", "Value"])
                writer.writerow(["Ministry Name", name])
                writer.writerow(["Total Programs", programs.count()])
                writer.writerow(
                    ["Active Programs", programs.filter(status="ACTIVE").count()])
                writer.writerow(["Total Applications", apps.count()])
                writer.writerow(["Unique Beneficiaries", apps.values(
                    "beneficiary").distinct().count()])
                writer.writerow([])
                writer.writerow(["Applications by Status"])
                writer.writerow(["Status", "Count"])
                for row in apps.values("status").annotate(count=Count("id")):
                    writer.writerow([row["status"], row["count"]])
                writer.writerow([])
                writer.writerow(["Applications by Program"])
                writer.writerow(
                    ["Program Name", "Total Applications", "Unique Beneficiaries"])
                for p in programs:
                    pa = apps.filter(program=p)
                    writer.writerow([p.name, pa.count(), pa.values(
                        "beneficiary").distinct().count()])
            return response
        except Exception as e:
            return err(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgramStatistics(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, program_id):
        try:
            if not is_ministry(request.user):
                return err("Only ministry users can view program statistics", status.HTTP_403_FORBIDDEN)
            program = get_object_or_404(Program, id=program_id)
            total = program.applications.count()
            unique = program.applications.values(
                "beneficiary").distinct().count()
            by_status = list(program.applications.values(
                "status").annotate(count=Count("id")).order_by("status"))
            by_charity_qs = ProgramApplication.objects.filter(program=program).values(
                "beneficiary__charity__id", "beneficiary__charity__name"
            ).annotate(
                beneficiary_count=Count("beneficiary", distinct=True), application_count=Count("id")
            ).order_by("-beneficiary_count")
            
            by_charity = [{
                "charity_id": r["beneficiary__charity__id"],
                "charity_name": r["beneficiary__charity__name"],
                "beneficiary_count": r["beneficiary_count"],
                "application_count": r["application_count"],
            } for r in by_charity_qs]
            return Response({
                "program_id": program.id,
                "program_name": program.name,
                "total_applications": total,
                "unique_beneficiaries": unique,
                "applications_by_status": by_status,
                "beneficiaries_by_charity": by_charity
            }, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return err(str(e), status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return err(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class CharityStatistics(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            if not (user.is_superuser or hasattr(user, "charity_admin")):
                return err("Only charity admins can view charity statistics", status.HTTP_403_FORBIDDEN)

            charity = getattr(user, "charity_admin", None)
            if user.is_superuser and not charity:
                charity_id = request.query_params.get("charity_id")
                if charity_id:
                    charity = get_object_or_404(Charity, id=charity_id)
            if not charity:
                return err("Charity not found", status.HTTP_400_BAD_REQUEST)

            event_id = request.query_params.get("event_id")
            status_filter = request.query_params.get("status")
            date_from = parse_date(request.query_params.get("date_from"))
            date_to = parse_date(request.query_params.get("date_to"))

            beneficiaries = Beneficiary.objects.filter(charity=charity)
            total_beneficiaries = beneficiaries.count()
            active_beneficiaries = beneficiaries.filter(is_active=True).count()

            events_qs = Event.objects.filter(charity=charity)
            if event_id:
                events_qs = events_qs.filter(id=event_id)

            regs = EventRegistration.objects.filter(event__charity=charity)
            if event_id:
                regs = regs.filter(event_id=event_id)
            if date_from:
                regs = regs.filter(registered_at__date__gte=date_from)
            if date_to:
                regs = regs.filter(registered_at__date__lte=date_to)

            apps = ProgramApplication.objects.filter(
                beneficiary__charity=charity)
            if status_filter:
                apps = apps.filter(status=status_filter)
            if date_from:
                apps = apps.filter(submitted_at__date__gte=date_from)
            if date_to:
                apps = apps.filter(submitted_at__date__lte=date_to)

            events_summary = []
            for ev in events_qs:
                total_registrations = EventRegistration.objects.filter(
                    event=ev).count()
                attended_count = EventRegistration.objects.filter(
                    event=ev, attended=True).count()
                available_spots = (None if ev.max_capacity is None else max(
                    0, ev.max_capacity - total_registrations))
                events_summary.append({
                    "id": ev.id,
                    "title": ev.title,
                    "event_date": ev.event_date.isoformat() if ev.event_date else None,
                    "is_active": ev.is_active,
                    "max_capacity": ev.max_capacity,
                    "current_registrations": total_registrations,
                    "available_spots": available_spots,
                    "total_registrations": total_registrations,
                    "attended_count": attended_count,
                })

            registrations_over_time = [
                {
                    "date": (timezone.now().date()-timedelta(days=29-i)).strftime("%Y-%m-%d"),
                    "day": (timezone.now().date()-timedelta(days=29-i)).strftime("%d/%m"),
                    "count": regs.filter(registered_at__date=(timezone.now().date()-timedelta(days=29-i))).count()
                } for i in range(30)
            ]

            upcoming = Event.objects.filter(
                charity=charity, event_date__gte=timezone.now(),
                event_date__lte=timezone.now()+timedelta(days=7), is_active=True
            ).order_by("event_date")[:5]
            upcoming_data = []
            for e in upcoming:
                total_registrations = EventRegistration.objects.filter(
                    event=e).count()
                upcoming_data.append({
                    "id": e.id,
                    "title": e.title,
                    "event_date": e.event_date.isoformat() if e.event_date else None,
                    "location": e.location,
                    "current_registrations": total_registrations,
                    "max_capacity": e.max_capacity
                })

            statistics = {
                "charity_name": charity.name,
                "charity_id": charity.id,
                "total_beneficiaries": total_beneficiaries,
                "active_beneficiaries": active_beneficiaries,
                "inactive_beneficiaries": total_beneficiaries - active_beneficiaries,
                "total_events": events_qs.count(),
                "active_events": events_qs.filter(is_active=True).count(),
                "inactive_events": events_qs.filter(is_active=False).count(),
                "total_registrations": regs.count(),
                "attended_registrations": regs.filter(attended=True).count(),
                "attendance_rate": round((regs.filter(attended=True).count()/regs.count()*100), 1) if regs.count() else 0,
                "total_applications": apps.count(),
                "applications_by_status": list(apps.values("status").annotate(count=Count("id")).order_by("status")),
                "events_summary": events_summary,
                "registrations_by_event": list(regs.values("event__id", "event__title").annotate(count=Count("id")).order_by("-count")),
                "registrations_over_time": registrations_over_time,
                "applications_by_program": list(apps.values("program__id", "program__name").annotate(count=Count("id")).order_by("-count")),
                "upcoming_events": upcoming_data,
                "filters_applied": {
                    "event_id": event_id, "status": status_filter,
                    "date_from": request.query_params.get("date_from"),
                    "date_to": request.query_params.get("date_to"),
                }
            }
            return Response(statistics, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return err(str(e), status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return err(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            user = request.user
            if not (user.is_superuser or hasattr(user, "charity_admin")):
                return err("Only charity admins can export statistics", status.HTTP_403_FORBIDDEN)

            charity = getattr(user, "charity_admin", None)
            if user.is_superuser and not charity:
                charity_id = request.data.get("charity_id")
                if charity_id:
                    charity = get_object_or_404(Charity, id=charity_id)
            if not charity:
                return err("Charity not found", status.HTTP_400_BAD_REQUEST)

            event_id = request.data.get("event_id")
            status_filter = request.data.get("status")
            date_from = parse_date(request.data.get("date_from"))
            date_to = parse_date(request.data.get("date_to"))
            export_type = request.data.get("export_type", "all")

            events_qs = Event.objects.filter(charity=charity)
            if event_id:
                events_qs = events_qs.filter(id=event_id)

            regs = EventRegistration.objects.filter(event__charity=charity)\
                .select_related("event", "beneficiary", "beneficiary__user", "beneficiary__charity")
            if event_id:
                regs = regs.filter(event_id=event_id)
            if date_from:
                regs = regs.filter(registered_at__date__gte=date_from)
            if date_to:
                regs = regs.filter(registered_at__date__lte=date_to)

            apps = ProgramApplication.objects.filter(beneficiary__charity=charity)\
                .select_related("program", "beneficiary", "beneficiary__user", "beneficiary__charity")
            if status_filter:
                apps = apps.filter(status=status_filter)
            if date_from:
                apps = apps.filter(submitted_at__date__gte=date_from)
            if date_to:
                apps = apps.filter(submitted_at__date__lte=date_to)

            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="charity_statistics_{charity.name.replace(" ", "_")}_{timezone.now().strftime("%Y%m%d")}.csv"'
            )
            writer = csv.writer(response)

            if export_type == "all":
                writer.writerow(["=== CHARITY STATISTICS SUMMARY ==="])
                writer.writerow([])
                writer.writerow(["Statistic", "Value"])
                writer.writerow(["Charity Name", charity.name])
                writer.writerow(
                    ["Total Beneficiaries", Beneficiary.objects.filter(charity=charity).count()])
                writer.writerow(["Active Beneficiaries", Beneficiary.objects.filter(
                    charity=charity, is_active=True).count()])
                writer.writerow(["Total Events", events_qs.count()])
                writer.writerow(
                    ["Active Events", events_qs.filter(is_active=True).count()])
                writer.writerow(["Total Registrations", regs.count()])
                writer.writerow(["Attended Registrations",
                                regs.filter(attended=True).count()])
                writer.writerow(["Total Applications", apps.count()])
                writer.writerow([])
                writer.writerow(["Applications by Status"])
                for s in apps.values("status").annotate(count=Count("id")):
                    writer.writerow([s["status"], s["count"]])

                writer.writerow([])
                writer.writerow(["=== EVENTS SUMMARY ==="])
                writer.writerow(["Event ID", "Event Title", "Event Date", "Location", "City",
                                 "Max Capacity", "Current Registrations", "Available Spots", "Status"])
                for e in events_qs:
                    total_registrations = EventRegistration.objects.filter(
                        event=e).count()
                    available_spots = (None if e.max_capacity is None else max(
                        0, e.max_capacity - total_registrations))
                    writer.writerow([
                        e.id, e.title,
                        e.event_date.strftime(
                            "%Y-%m-%d %H:%M") if e.event_date else "",
                        e.location, e.city, e.max_capacity, total_registrations,
                        available_spots, "Active" if e.is_active else "Inactive"
                    ])

                writer.writerow([])
                writer.writerow(["=== EVENT REGISTRATIONS ==="])
                writer.writerow(["Registration ID", "Event Title", "Event Date", "Event Location",
                                 "Beneficiary Name", "National ID", "Registered Date", "Attended", "Notes"])
                for r in regs:
                    name = f"{r.beneficiary.user.first_name} {r.beneficiary.user.last_name}".strip(
                    ) if r.beneficiary and r.beneficiary.user else ""
                    nid = r.beneficiary.national_id or "" if r.beneficiary else ""
                    writer.writerow([
                        r.id, r.event.title if r.event else "",
                        r.event.event_date.strftime(
                            "%Y-%m-%d %H:%M") if r.event and r.event.event_date else "",
                        r.event.location if r.event else "", name, nid,
                        r.registered_at.strftime(
                            "%Y-%m-%d %H:%M") if r.registered_at else "",
                        "Yes" if r.attended else "No", r.notes or ""
                    ])

                writer.writerow([])
                writer.writerow(["=== PROGRAM APPLICATIONS ==="])
                writer.writerow(["Application ID", "Program Name", "Beneficiary Name", "National ID",
                                 "Application Status", "Submitted Date", "Reviewed Date", "Review Notes"])
                for a in apps:
                    name = f"{a.beneficiary.user.first_name} {a.beneficiary.user.last_name}".strip(
                    ) if a.beneficiary and a.beneficiary.user else ""
                    nid = a.beneficiary.national_id or "" if a.beneficiary else ""
                    writer.writerow([
                        a.id, a.program.name if a.program else "", name, nid, a.status,
                        a.submitted_at.strftime(
                            "%Y-%m-%d %H:%M") if a.submitted_at else "",
                        a.reviewed_at.strftime(
                            "%Y-%m-%d %H:%M") if a.reviewed_at else "", a.review_notes or ""
                    ])

            elif export_type == "registrations":
                writer.writerow(["Registration ID", "Event Title", "Event Date", "Event Location",
                                 "Beneficiary Name", "National ID", "Registered Date", "Attended", "Notes"])
                for r in regs:
                    name = f"{r.beneficiary.user.first_name} {r.beneficiary.user.last_name}".strip(
                    ) if r.beneficiary and r.beneficiary.user else ""
                    nid = r.beneficiary.national_id or "" if r.beneficiary else ""
                    writer.writerow([
                        r.id, r.event.title if r.event else "",
                        r.event.event_date.strftime(
                            "%Y-%m-%d %H:%M") if r.event and r.event.event_date else "",
                        r.event.location if r.event else "", name, nid,
                        r.registered_at.strftime(
                            "%Y-%m-%d %H:%M") if r.registered_at else "",
                        "Yes" if r.attended else "No", r.notes or ""
                    ])

            elif export_type == "events":
                writer.writerow(["Event ID", "Event Title", "Event Date", "Location", "City",
                                 "Max Capacity", "Current Registrations", "Available Spots", "Status"])
                for e in events_qs:
                    total_registrations = EventRegistration.objects.filter(
                        event=e).count()
                    available_spots = (None if e.max_capacity is None else max(
                        0, e.max_capacity - total_registrations))
                    writer.writerow([
                        e.id, e.title,
                        e.event_date.strftime(
                            "%Y-%m-%d %H:%M") if e.event_date else "",
                        e.location, e.city, e.max_capacity, total_registrations,
                        available_spots, "Active" if e.is_active else "Inactive"
                    ])

            elif export_type == "applications":
                writer.writerow(["Application ID", "Program Name", "Beneficiary Name", "National ID",
                                 "Application Status", "Submitted Date", "Reviewed Date", "Review Notes"])
                for a in apps:
                    name = f"{a.beneficiary.user.first_name} {a.beneficiary.user.last_name}".strip(
                    ) if a.beneficiary and a.beneficiary.user else ""
                    nid = a.beneficiary.national_id or "" if a.beneficiary else ""
                    writer.writerow([
                        a.id, a.program.name if a.program else "", name, nid, a.status,
                        a.submitted_at.strftime(
                            "%Y-%m-%d %H:%M") if a.submitted_at else "",
                        a.reviewed_at.strftime(
                            "%Y-%m-%d %H:%M") if a.reviewed_at else "", a.review_notes or ""
                    ])

            else:
                writer.writerow(["Statistic", "Value"])
                writer.writerow(["Charity Name", charity.name])
                writer.writerow(
                    ["Total Beneficiaries", Beneficiary.objects.filter(charity=charity).count()])
                writer.writerow(["Active Beneficiaries", Beneficiary.objects.filter(
                    charity=charity, is_active=True).count()])
                writer.writerow(["Total Events", events_qs.count()])
                writer.writerow(
                    ["Active Events", events_qs.filter(is_active=True).count()])
                writer.writerow(["Total Registrations", regs.count()])
                writer.writerow(["Attended Registrations",
                                regs.filter(attended=True).count()])
                writer.writerow(["Total Applications", apps.count()])
                for s in apps.values("status").annotate(count=Count("id")):
                    writer.writerow(
                        [f'Applications - {s["status"]}', s["count"]])

            return response
        except PermissionDenied as e:
            return err(str(e), status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return err(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

