from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Charity, Beneficiary, Program, Event, EventRegistration, ProgramApplication


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password",
                  "first_name", "last_name", "is_superuser")


class CharitySerializer(serializers.ModelSerializer):
    admin_user = UserSerializer(read_only=True)

    class Meta:
        model = Charity
        fields = "__all__"


class BeneficiarySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    charity = serializers.PrimaryKeyRelatedField(
        queryset=Charity.objects.all(), required=False)

    class Meta:
        model = Beneficiary
        fields = "__all__"


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    
    charity_name = serializers.CharField(source='charity.name', read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = "__all__"


class ProgramApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProgramApplication
        fields = "__all__"
