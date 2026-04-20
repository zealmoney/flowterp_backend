from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Profile, SavedSetup, RecentFlow

from .models import Profile, SavedSetup

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "display_name",
            "bio",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "profile",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    display_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    bio = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "display_name",
            "bio",
        ]

    def validate_email(self, value):
        email = value.lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate_username(self, value):
        username = value.strip()
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return username

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        display_name = validated_data.pop("display_name", "")
        bio = validated_data.pop("bio", "")

        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=password,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        Profile.objects.create(
            user=user,
            display_name=display_name,
            bio=bio,
        )

        return user


class MeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "profile",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "date_joined"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile, _ = Profile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class SavedSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSetup
        fields = [
            "id",
            "name",
            "filters_json",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FlowTerpTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data

class RecentFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecentFlow
        fields = [
            "id",
            "name",
            "filters_json",
            "source",
            "last_used_at",
            "created_at",
        ]
        read_only_fields = ["id", "last_used_at", "created_at"]


class RecentFlowTrackSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    filters_json = serializers.JSONField()
    source = serializers.ChoiceField(choices=["preset", "manual", "saved_setup"])

    def validate_filters_json(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("filters_json must be an object.")
        return value