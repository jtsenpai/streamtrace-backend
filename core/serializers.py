from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Provider

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User(
            userName = validated_data["username"],
            email = validated_data.get("email", "").lower(),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
    
    def validate_email(self, value):
        if value and User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email already in use")
        return value
    
    def validate_userName(self, value):
        if User.objects.filter(userName=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value
    
class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProviderSerializer(serializers.ModelSerializer):
    # Django REST Framework (DRF) serializer
    # controls how Provider objects become JSON (and back).

    class Meta:
        model = Provider
        field = ["id", "name", "url", "logo_url", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str):
        # reject empty/space-only names
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Name cannot be empty.")
        return v